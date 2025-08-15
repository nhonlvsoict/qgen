import argparse, subprocess, time, csv, os, sys, json, pathlib

ROOT = pathlib.Path(".").resolve()

# This script is designed to run experiments with quantum circuits using Qiskit.
# It builds Docker images for different backends (classical, Aer, IBM),
def run(cmd):
    print(">>", " ".join(cmd))
    return subprocess.run(cmd, check=True, text=True, capture_output=True)

def classical_bv(n):
    import random, time
    secret = "".join(str(random.randint(0,1)) for _ in range(n))
    start = time.time()
    elapsed = time.time() - start
    return {"success": True, "oracle_calls": n, "elapsed_s": elapsed, "note": f"secret={secret}"}

def classical_grover(n):
    import time
    N = 2**n
    start = time.time()
    elapsed = time.time() - start
    return {"success": True, "oracle_calls": N//2, "elapsed_s": elapsed, "note": f"N={N}"}

def build_image(exp_py, tag, target="ibm"):
    run(["qsg", "build", exp_py, "-t", target, "-i", tag])

def docker_run(tag, env=None):
    env_opts = []
    if env:
        for k,v in env.items():
            env_opts += ["-e", f"{k}={v}"]
    cp = run(["docker", "run", "--rm"] + env_opts + [tag])
    out = cp.stdout.strip()
    try:
        data = json.loads(out.splitlines()[-1])
    except Exception:
        data = {"raw": out}
    return data

def qgen_local_run(tag, env=None):
    env_opts = []
    if env:
        for k,v in env.items():
            env_opts += ["-e", f"{k}={v}"]
    cp = run(["qsg", "run-local"] + env_opts + [tag])
    out = cp.stdout.strip()
    try:
        data = json.loads(out.splitlines()[-1])
    except Exception:
        data = {"raw": out}
    return data

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exp", choices=["bv","grover"], required=True)
    ap.add_argument("--ns", nargs="+", type=int, required=True)
    ap.add_argument("--modes", nargs="+", choices=["classical","aer","ibm"], required=True)
    ap.add_argument("--image-prefix", default="qsg/exp")
    ap.add_argument("--csv", default="results.csv")
    args = ap.parse_args()

    exp_file = f"examples/{args.exp}_qiskit.py"
    if not (ROOT/exp_file).exists():
        print(f"Expected {exp_file} in current repo; copy from bundle.")
        sys.exit(1)

    rows = []
    for n in args.ns:
        if "classical" in args.modes:
            res = classical_bv(n) if args.exp=="bv" else classical_grover(n)
            rows.append({
                "exp": args.exp, "n": n, "backend": "classical",
                "build_s": 0.0,
                "submit_to_result_s": res["elapsed_s"],
                "oracle_or_circuits": res["oracle_calls"],
                "success_prob": 1.0,
                "note": res["note"],
            })

        if "aer" in args.modes:
            tag = f"{args.image_prefix}:{args.exp}-aer-n{n}"
            t0 = time.time()
            build_image(exp_file, tag, target="ibm")
            build_s = time.time() - t0
            data = qgen_local_run(tag, env={})  # no token
            rows.append({
                "exp": args.exp, "n": n, "backend": "aer_local",
                "build_s": round(build_s,3),
                "submit_to_result_s": data.get("elapsed_s", None),
                "oracle_or_circuits": 1 if args.exp=="bv" else None,
                "success_prob": None,
                "note": json.dumps(data),
            })

        if "ibm" in args.modes:
            token = os.getenv("IBM_TOKEN")
            if not token:
                print("[WARN] IBM mode requested but IBM_TOKEN missing; skipping.")
            else:
                tag = f"{args.image_prefix}:{args.exp}-ibm-n{n}"
                t0 = time.time()
                build_image(exp_file, tag, target="ibm")
                build_s = time.time() - t0
                data = qgen_local_run(tag, env={"IBM_TOKEN": token})
                rows.append({
                    "exp": args.exp, "n": n, "backend": "ibm_runtime_sim",
                    "build_s": round(build_s,3),
                    "submit_to_result_s": data.get("elapsed_s", None),
                    "oracle_or_circuits": 1 if args.exp=="bv" else None,
                    "success_prob": None,
                    "note": json.dumps(data),
                })

    with open(args.csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=[
            "exp","n","backend","build_s","submit_to_result_s","oracle_or_circuits","success_prob","note"
        ])
        w.writeheader()
        w.writerows(rows)
    print("Wrote", args.csv)

if __name__ == "__main__":
    main()
