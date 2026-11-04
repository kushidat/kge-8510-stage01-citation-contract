#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""8504/8510 v1.1 isolated, OFFLINE-only two-direction file-spool transport.

8504 owns sqlite registry and trusted authority. Worker must NEVER mount DB.
This module has NO provider, socket, subprocess, key, data-loader or scientific
assessment code. File permissions / mount isolation must be independently proven.
Any imported response has UNVERIFIED provenance and stays REVIEW_HOLD even
if the caller's pinned 8504 schema+authority gate returns a contract receipt.
"""
from __future__ import annotations
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import sqlite3
import stat
from typing import Any, Callable, Mapping

PROTOCOL = 'KGE_V11_8504_8510_FILE_SPOOL_V0_1_OFFLINE'
REQUEST_KIND = 'KGE_V11_REQUEST'
RESPONSE_KIND = 'KGE_V11_OFFLINE_IMPORTED_RESPONSE'
ALLOWED_ORIGIN = 'UNVERIFIED_OFFLINE_BYTES'
MAX_PAYLOAD = 16 * 1024 * 1024
MAX_PROMPT = 32 * 1024
MAX_SCHEMA = 64 * 1024
MAX_RESPONSE = 256 * 1024
MAX_REQUEST_ENVELOPE = MAX_PAYLOAD + MAX_PROMPT * 2 + MAX_SCHEMA * 2 + 1024 * 1024
MAX_RESPONSE_ENVELOPE = MAX_RESPONSE * 2 + 8192
SCHEMA_SHA256 = '52f291d46fec0a2621d53de86221ad6d977b029d3a5ed7e90643b796a1191fdf'
PROMPT_SHA256 = 'fa6b0db4776104088f7a7fc4587321be3d843d0bf965d37536939440a7e37c30'
FAMILIES = frozenset(('node2vec','TransE','RotatE','ComplEx','RDF2Vec','CompGCN'))
_HEX64 = re.compile(r'[0-9a-f]{64}\Z')
_REQUEST_ID = re.compile(r'[0-9a-f]{32}\Z')

class BoundaryHold(Exception):
    """Fail-closed code-only diagnostic. Never include Evidence text or secrets."""
    pass

def require(value: bool, code: str) -> None:
    if not value:
        raise BoundaryHold(code)

def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()

def canonical_json(obj: Any) -> bytes:
    try:
        return json.dumps(obj, ensure_ascii=False, sort_keys=True,
                          separators=(',', ':'), allow_nan=False).encode('utf-8')
    except (TypeError, ValueError, RecursionError):
        raise BoundaryHold('NOT_CANONICAL_JSON') from None

def strict_json(raw: bytes, cap: int) -> dict:
    require(type(raw) is bytes and 0 < len(raw) <= cap, 'JSON_INPUT_SIZE_REJECTED')
    def pairs(ps):
        result={}
        for k, v in ps:
            if k in result:
                raise BoundaryHold('DUPLICATE_JSON_KEY')
            result[k]=v
        return result
    def bad_constant(_):
        raise BoundaryHold('NONFINITE_JSON')
    try:
        obj=json.loads(raw.decode('utf-8', 'strict'), object_pairs_hook=pairs,
                       parse_constant=bad_constant)
    except BoundaryHold:
        raise
    except (ValueError,UnicodeError,TypeError,RecursionError):
        raise BoundaryHold('MALFORMED_JSON') from None
    require(type(obj) is dict, 'JSON_TOP_NOT_OBJECT')
    return obj

def identity(payload: Mapping[str, Any]) -> dict:
    require(type(payload) is dict and set(payload)=={'task','constraints','evidence_bundle'},
            'INPUT_PAYLOAD_SHAPE_REJECTED')
    bundle=payload.get('evidence_bundle')
    require(type(bundle) is dict, 'MISSING_EVIDENCE_BUNDLE')
    ide=bundle.get('identity')
    rank=bundle.get('ranking')
    require(type(ide) is dict and type(rank) is dict, 'BUNDLE_IDENTITY_MISSING')
    ans={k:ide.get(k) for k in ('disease_iri','mouse_iri')}
    ans['family']=rank.get('family')
    ans['final_rank']=rank.get('final_rank')
    require(all(type(ans[k]) is str and len(ans[k])<2048 and ans[k] for k in ('disease_iri','mouse_iri')),
            'INVALID_IRI_IDENTITY')
    require(type(ans['family']) is str and ans['family'] in FAMILIES,'INVALID_FAMILY')
    require(type(ans['final_rank']) is int and 1<=ans['final_rank']<=5892,'INVALID_RANK')
    require(bundle.get('assessment',{}).get('formal_assessment_boundary',{}).get('formal_state_mutated') is False,
            'FORMAL_BOUNDARY_NOT_FROZEN')
    return ans

def require_plain_dir(path: Path) -> None:
    require(path.is_absolute(), 'RELATIVE_PATH_REJECTED')
    require(path.is_dir() and not path.is_symlink(), 'SPOOL_DIR_MISSING_OR_SYMLINK')
    # Reject symlink ancestors; do not resolve an attacker-controlled alternate path.
    for parent in (path, *path.parents):
        require(not parent.is_symlink(), 'SYMLINK_ANCESTOR_REJECTED')

def read_regular(path: Path, size: int) -> bytes:
    require(path.is_absolute() and not path.is_symlink() and path.is_file(),
            'SOURCE_FILE_MISSING_OR_SYMLINK')
    try:
        fd=os.open(path, os.O_RDONLY | getattr(os,'O_NOFOLLOW',0))
        try:
            meta=os.fstat(fd)
            require(stat.S_ISREG(meta.st_mode) and 0<meta.st_size<=size,'SOURCE_SIZE_DENIED')
            with os.fdopen(fd,'rb',closefd=False) as f:
                raw=f.read(size+1)
            require(len(raw)<=size and len(raw)==meta.st_size,'SOURCE_SIZE_CHANGED')
            return raw
        finally:
            os.close(fd)
    except (OSError, PermissionError):
        raise BoundaryHold('READ_NOT_ALLOWED') from None

def atomically_create_new(directory: Path, basename: str, content: bytes) -> Path:
    require_plain_dir(directory)
    require(re.fullmatch(r'[A-Za-z0-9_.-]{1,100}',basename) is not None,'BAD_QUEUE_FILENAME')
    final=directory/basename
    require(not final.exists() and not final.is_symlink(), 'DESTINATION_ALREADY_EXISTS')
    tmp=directory/('.tmp-'+secrets.token_hex(16))
    try:
        fd=os.open(tmp,os.O_WRONLY|os.O_CREAT|os.O_EXCL|getattr(os,'O_NOFOLLOW',0),0o600)
        with os.fdopen(fd,'wb') as f:
            f.write(content)
            f.flush();os.fsync(f.fileno())
        # Hard-link is an atomic no-overwrite publish operation on the same FS.
        # Unlike os.replace(), it cannot overwrite a preexisting target.
        os.link(tmp,final)
        require(read_regular(final,len(content))==content,'PUBLISHED_BYTES_MISMATCH')
        return final
    except FileExistsError:
        raise BoundaryHold('DESTINATION_ALREADY_EXISTS') from None
    except (OSError,PermissionError):
        raise BoundaryHold('SPOOL_PUBLISH_DENIED') from None
    finally:
        try:tmp.unlink(missing_ok=True)
        except OSError:pass

def _registered_db(dbfile:Path) -> sqlite3.Connection:
    require(dbfile.is_absolute() and dbfile.exists() and not dbfile.is_symlink(),
            'PRIVATE_DB_MISSING_OR_SYMLINK')
    require_plain_dir(dbfile.parent)
    conn=sqlite3.connect(f'file:{dbfile}?mode=rw',uri=True, timeout=5)
    conn.execute('PRAGMA busy_timeout=5000')
    return conn

def init_8504_private_db(dbfile:Path) -> None:
    """Explicit operator-only creation, never called by an import or worker."""
    require_plain_dir(dbfile.parent)
    require(not dbfile.exists() and not dbfile.is_symlink(),'PRIVATE_DB_EXISTS')
    # sqlite may create aux journals only under explicitly private dir.
    conn=sqlite3.connect(f'file:{dbfile}?mode=rwc',uri=True)
    try:
        conn.execute('''CREATE TABLE requests (
            request_id TEXT PRIMARY KEY, request_sha TEXT NOT NULL,
            payload_sha TEXT NOT NULL, prompt_sha TEXT NOT NULL,
            schema_sha TEXT NOT NULL, identity_json TEXT NOT NULL,
            state TEXT NOT NULL CHECK (state IN ('PENDING','REVIEW_HOLD'))
        )''')
        conn.commit()
    finally:conn.close()
    os.chmod(dbfile,0o600)

def request_from_8504(*, payload:dict, prompt_bytes:bytes, schema_bytes:bytes,
                      request_dir:Path, private_db:Path,
                      assert_live_bundle:Callable[[dict],None],
                      request_id:str|None=None) -> dict:
    """Only invoke from trusted 8504 context with live ranking authority.

    `assert_live_bundle` MUST call the pinned
    assert_live_evidence_bundle(authority=..., bundle=...) in-process.
    Transport itself is not an authority and never serializes authority.
    """
    require(callable(assert_live_bundle),'TRUSTED_AUTHORITY_CHECK_REQUIRED')
    ide=identity(payload)
    assert_live_bundle(payload['evidence_bundle'])  # exceptions => fail closed
    require(type(prompt_bytes) is bytes and 0<len(prompt_bytes)<=MAX_PROMPT,
            'PROMPT_SIZE_REJECTED')
    require(type(schema_bytes) is bytes and 0<len(schema_bytes)<=MAX_SCHEMA,
            'SCHEMA_SIZE_REJECTED')
    require(sha(prompt_bytes)==PROMPT_SHA256,'PROMPT_SHA_MISMATCH')
    require(sha(schema_bytes)==SCHEMA_SHA256,'SCHEMA_SHA_MISMATCH')
    schema=strict_json(schema_bytes,MAX_SCHEMA)
    require(len(schema.get('required',[]))==15 and len(schema.get('properties',{}))==15,
            'FIFTEEN_FIELD_CONTRACT_REJECTED')
    raw_payload=canonical_json(payload)
    require(0<len(raw_payload)<=MAX_PAYLOAD,'PAYLOAD_TOO_LARGE')
    request_id=request_id or secrets.token_hex(16)
    require(_REQUEST_ID.fullmatch(request_id) is not None,'REQUEST_ID_INVALID')
    request={
        'kind':REQUEST_KIND,'protocol':PROTOCOL, 'request_id':request_id,
        'candidate_identity':ide,'payload_sha256':sha(raw_payload),
        'prompt_sha256':sha(prompt_bytes), 'schema_sha256':sha(schema_bytes),
        'payload':payload,
        'prompt_base64':base64.b64encode(prompt_bytes).decode('ascii'),
        'schema_base64':base64.b64encode(schema_bytes).decode('ascii'),
        'requested_external_send':False, 'provider_execution_authorized':False,
        'source_auth_claim':'8504_PROCESS_LOCAL_AUTHORITY_NOT_TRANSFERRED'
    }
    raw=canonical_json(request)
    require(len(raw)<=MAX_REQUEST_ENVELOPE,'REQUEST_ENVELOPE_TOO_LARGE')
    require_plain_dir(request_dir)
    with _registered_db(private_db) as c:
        try:
            c.execute('INSERT INTO requests VALUES (?,?,?,?,?,?,?)',
                 (request_id,sha(raw),sha(raw_payload),sha(prompt_bytes),sha(schema_bytes),
                  canonical_json(ide).decode('utf-8'),'PENDING'))
            final=atomically_create_new(request_dir,request_id+'.json',raw)
            require(read_regular(final,MAX_REQUEST_ENVELOPE)==raw,'REQUEST_PUBLISH_MISMATCH')
        except sqlite3.IntegrityError:
            raise BoundaryHold('REQUEST_ID_ALREADY_REGISTERED') from None
    return {'request_id':request_id,'status':'PENDING_OFFLINE_NO_PROVIDER',
            'request_sha256':sha(raw),'payload_sha256':sha(raw_payload),
            'candidate_identity':ide}

def parse_request_for_8510(raw:bytes) -> dict:
    r=strict_json(raw,MAX_REQUEST_ENVELOPE)
    require(set(r)=={'kind','protocol','request_id','candidate_identity','payload_sha256',
                    'prompt_sha256','schema_sha256','payload','prompt_base64','schema_base64',
                    'requested_external_send','provider_execution_authorized','source_auth_claim'},
            'REQUEST_ENVELOPE_FIELDS_REJECTED')
    require(r['kind']==REQUEST_KIND and r['protocol']==PROTOCOL,'REQUEST_PROTOCOL_REJECTED')
    require(type(r['request_id']) is str and _REQUEST_ID.fullmatch(r['request_id']) is not None,
            'REQUEST_ID_INVALID')
    require(r['requested_external_send'] is False and r['provider_execution_authorized'] is False,
            'EXTERNAL_SEND_NOT_AUTHORIZED')
    require(r['source_auth_claim']=='8504_PROCESS_LOCAL_AUTHORITY_NOT_TRANSFERRED',
            'AUTHORITY_TRANSFER_CLAIM_DENIED')
    payload=r['payload']; require(type(payload) is dict,'REQUEST_PAYLOAD_NOT_OBJECT')
    require(identity(payload)==r['candidate_identity'],'REQUEST_IDENTITY_MISMATCH')
    require(sha(canonical_json(payload))==r['payload_sha256'],'REQUEST_PAYLOAD_SHA_MISMATCH')
    try:
        prompt=base64.b64decode(r['prompt_base64'],validate=True)
        schema=base64.b64decode(r['schema_base64'],validate=True)
    except (ValueError,TypeError):
        raise BoundaryHold('BASE64_BYTES_INVALID') from None
    require(len(prompt)<=MAX_PROMPT and sha(prompt)==PROMPT_SHA256==r['prompt_sha256'],
            'REQUEST_PROMPT_PIN_FAILED')
    require(len(schema)<=MAX_SCHEMA and sha(schema)==SCHEMA_SHA256==r['schema_sha256'],
            'REQUEST_SCHEMA_PIN_FAILED')
    return r

def import_offline_8510_response(*, request_dir:Path, response_dir:Path,
                                  request_id:str, response_raw:bytes) -> dict:
    """Manually imported offline JSON only; no model provenance / API claim."""
    require(type(request_id) is str and _REQUEST_ID.fullmatch(request_id) is not None,
            'REQUEST_ID_INVALID')
    require_plain_dir(request_dir);require_plain_dir(response_dir)
    request_raw=read_regular(request_dir/(request_id+'.json'),MAX_REQUEST_ENVELOPE)
    request=parse_request_for_8510(request_raw)
    require(type(response_raw) is bytes and 0<len(response_raw)<=MAX_RESPONSE,
            'RESPONSE_SIZE_REJECTED')
    parsed=strict_json(response_raw,MAX_RESPONSE)
    # This is a technical prefilter. Only 8504's in-process pinned gate decides.
    require(set(parsed.get('candidate_identity',{}))==set(request['candidate_identity']) and
            parsed.get('candidate_identity')==request['candidate_identity'],
            'RESPONSE_CANDIDATE_IDENTITY_REJECTED')
    event={'kind':RESPONSE_KIND,'protocol':PROTOCOL,'request_id':request_id,
           'request_sha256':sha(request_raw),'payload_sha256':request['payload_sha256'],
           'response_sha256':sha(response_raw),'response_base64':base64.b64encode(response_raw).decode('ascii'),
           'source_status':ALLOWED_ORIGIN,'model_id':None,'execution_timestamp':None,
           'provider_call':False,'external_send':False,'formal_assessment_mutated':False}
    data=canonical_json(event)
    require(len(data)<=MAX_RESPONSE_ENVELOPE,'RESPONSE_ENVELOPE_TOO_LARGE')
    atomically_create_new(response_dir,request_id+'.json',data)
    return {'request_id':request_id,'offline_response':'PUBLISHED_UNVERIFIED_REVIEW_ONLY',
            'response_sha256':sha(response_raw)}

def review_8504_response(*, request_id:str, request_dir:Path, response_dir:Path,
                          private_db:Path, current_payload:dict, schema_path:Path,
                          assert_live_bundle:Callable[[dict],None],
                          pinned_gate:Callable[...,dict]) -> tuple[dict,dict]:
    """8504 trust boundary. NEVER mark scientific evidence or provider verified."""
    require(type(request_id) is str and _REQUEST_ID.fullmatch(request_id) is not None,
            'REQUEST_ID_INVALID')
    require(callable(assert_live_bundle) and callable(pinned_gate),
            'MISSING_PINNED_GATE_OR_AUTHORITY')
    current_ide=identity(current_payload)
    assert_live_bundle(current_payload['evidence_bundle'])
    with _registered_db(private_db) as c:
        row=c.execute('SELECT request_sha,payload_sha,prompt_sha,schema_sha,identity_json,state '
                      'FROM requests WHERE request_id=?',(request_id,)).fetchone()
    require(row is not None and row[-1]=='PENDING','REQUEST_NOT_PENDING_OR_UNKNOWN')
    rq=read_regular(request_dir/(request_id+'.json'),MAX_REQUEST_ENVELOPE)
    require(sha(rq)==row[0],'QUEUED_REQUEST_SHA_DIFFERS_FROM_PRIVATE_DB')
    parsed=parse_request_for_8510(rq)
    require(parsed['candidate_identity']==current_ide==strict_json(row[4].encode(),8192),
            'REQUEST_CURRENT_IDENTITY_MISMATCH')
    require(sha(canonical_json(current_payload))==row[1]==parsed['payload_sha256'],
            'REBUILT_PAYLOAD_SHA_MISMATCH')
    require(row[2]==PROMPT_SHA256 and row[3]==SCHEMA_SHA256,'PINNED_ASSET_SHA_MISMATCH')
    ev=strict_json(read_regular(response_dir/(request_id+'.json'),MAX_RESPONSE_ENVELOPE),
                   MAX_RESPONSE_ENVELOPE)
    require(set(ev)=={'kind','protocol','request_id','request_sha256','payload_sha256',
                     'response_sha256','response_base64','source_status','model_id',
                     'execution_timestamp','provider_call','external_send',
                     'formal_assessment_mutated'},'RESPONSE_FIELDS_REJECTED')
    require(ev['kind']==RESPONSE_KIND and ev['protocol']==PROTOCOL and ev['request_id']==request_id
            and ev['request_sha256']==row[0] and ev['payload_sha256']==row[1],
            'RESPONSE_REQUEST_BINDING_REJECTED')
    require(ev['source_status']==ALLOWED_ORIGIN and ev['model_id'] is None
            and ev['execution_timestamp'] is None and ev['provider_call'] is False
            and ev['external_send'] is False and ev['formal_assessment_mutated'] is False,
            'RESPONSE_PROVIDER_OR_FORMAL_CLAIM_REJECTED')
    try: out_raw=base64.b64decode(ev['response_base64'],validate=True)
    except (ValueError,TypeError):raise BoundaryHold('RESPONSE_BASE64_BAD') from None
    require(sha(out_raw)==ev['response_sha256'],'RESPONSE_BYTES_SHA_MISMATCH')
    output=strict_json(out_raw,MAX_RESPONSE)
    # The caller's gate MUST use fresh process-local authority and exact schema.
    receipt=pinned_gate(output,current_payload,schema_path)
    require(type(receipt) is dict,'PINNED_GATE_RECEIPT_INVALID')
    with _registered_db(private_db) as c:
        n=c.execute("UPDATE requests SET state='REVIEW_HOLD' WHERE request_id=? AND state='PENDING'",
                    (request_id,)).rowcount
        require(n==1,'REQUEST_REPLAY_OR_STATE_CHANGED')
    return output,{'status':'UNVERIFIED_OFFLINE_TEXT_REVIEW_HOLD',
                   'source_status':ALLOWED_ORIGIN,'provider_verified':False,
                   'scientific_support_verified':False,'formal_assessment_mutated':False,
                   'request_id':request_id,'contract_receipt':receipt}
