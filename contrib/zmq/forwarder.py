import logging
import os
import uuid
import zmq
import zmq.auth
from zmq.auth.thread import ThreadAuthenticator

level=logging.DEBUG
logging.basicConfig(level=level, format="[%(levelname)s] %(message)s")

base_dir = os.path.dirname(__file__)
keys_dir = os.path.join(base_dir, '..', '..', 'keys/')
private_key = os.path.join(keys_dir, "server.key_secret")

#if not (os.path.exists(private_key)):
#    if not (os.path.exists(keys_dir)):
#        os.makedirs(keys_dir)
#    zmq.auth.create_certificates(keys_dir, basename)

ctx = zmq.Context()

auth = ThreadAuthenticator(ctx)
auth.start()
# FIXME reload keys without restarting process
auth.configure_curve(domain='*', location=keys_dir)

curve_publickey, curve_secretkey = zmq.auth.load_certificate(private_key)

sub = ctx.socket(zmq.XSUB)
sub.curve_publickey = curve_publickey
sub.curve_secretkey = curve_secretkey
sub.curve_server = True

pub = ctx.socket(zmq.XPUB)
pub.curve_publickey = curve_publickey
pub.curve_secretkey = curve_secretkey
pub.curve_server = True

sub.bind("tcp://*:5555")
pub.bind("tcp://*:5566")

zmq.proxy(pub, sub)

auth.stop()
sub.close()
pub.close()
ctx.term()