from spinqit import get_compiler
from spinqit.backend import get_spinq_cloud,SpinQCloudConfig
from spinqit.model import Circuit
from spinqit import H, CNOT, CZ, I
import time, datetime
from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_v1_5 as Signature_pkcs1_v1_5
from Crypto.PublicKey import RSA
import base64

username = "spinq"
keyfile = "/spinq.pub"
# login to SpinQCloudBackend``
#backend = get_spinq_cloud(username, None, %SPINQIT_JUPYTER_TOKEN) # specify the token, only for jupyter notebook
backend = get_spinq_cloud(username, keyfile)
print(backend)
gemini = backend.get_platform("gemini_vp")

print(gemini.available())
if gemini.available():
    comp = get_compiler("native")
    circ = Circuit()
    q = circ.allocateQubits(2)
    circ << (H, q[0])
    ir = comp.compile(circ,0)
    config = SpinQCloudConfig()
    config.configure_platform('gemini_vp')
    config.configure_shots(1024)
    config.configure_task('newapitest2','newapi')
    res = backend.execute(ir,config)

    print(res.probabilities)
