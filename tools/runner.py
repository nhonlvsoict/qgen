# tools/runner.py  — replace entire file
import argparse, subprocess, time, csv, os, sys, json, pathlib, random

ROOT = pathlib.Path(".").resolve()

def run(cmd, env=None):
    print(">>", " ".join(cmd))
    return subprocess.run(cmd, check=True, text=True, capture_output=True, env=env)

def classical_bv(n: int, secret: str):
    import time
    def oracle(x_bits: str) -> int:
        return sum(int(b) & int(s) for b, s in zip(x_bits, secret)) % 2
    start = time.time()
    recovered = []
    oracle_calls = 0
    for i in range(n):
        x = ["0"] * n
        x[n - 1 - i] = "1"
        bit = oracle("".join(x))
        recovered.append(str(bit))
        oracle_calls += 1
    recovered = "".join(recovered[::-1])
    elapsed = time.time() - start
    return {"success": (recovered == secret), "oracle_calls": oracle_calls, "elapsed_s": elapsed,
            "note": f"secret={secret}, recovered={recovered}"}

def classical_grover(n: int, marked: str):
    import time
    from itertools import product
    candidates = ["".join(bits) for bits in product("01", repeat=n)]
    random.shuffle(candidates)
    def oracle(c: str) -> bool: return c == marked
    start = time.time(); oracle_calls = 0; found = None
    for c in candidates:
        oracle_calls += 1
        if oracle(c):
            found = c; break
    elapsed = time.time() - start
    return {"success": (found == marked), "oracle_calls": oracle_calls, "elapsed_s": elapsed,
            "note": f"marked={marked}, found={found}"}

def build_image(exp_py, tag, target, env_vars):
    build_env = os.environ.copy()
    build_env.update(env_vars or {})
    run(["qsg", "build", exp_py, "-t", target, "-i", tag], env=build_env)

def docker_run(tag, env=None):
    env_opts = []
    if env:
        for k,v in env.items(): env_opts += ["-e", f"{k}={v}"]
    cp = run(["docker", "run", "--rm"] + env_opts + [tag])
    out = cp.stdout.strip()
    try: return json.loads(out.splitlines()[-1])
    except Exception: return {"raw": out}

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
        print(f"Expected {exp_file}; copy from examples in the bundle.")
        sys.exit(1)

    rows = []
    for n in args.ns:
        # Create the same secret/marked for all backends
        if args.exp == "bv":
            secret = "".join(str(random.randint(0,1)) for _ in range(n))
            params = {"QGEN_N": str(n), "QGEN_SECRET": secret}
        else:
            marked = "".join(str(random.randint(0,1)) for _ in range(n))
            params = {"QGEN_N": str(n), "QGEN_MARKED": marked}

        # Classical
        if "classical" in args.modes:
            res = classical_bv(n, secret) if args.exp=="bv" else classical_grover(n, marked)
            rows.append({
                "exp": args.exp, "n": n, "backend": "classical",
                "build_s": 0.0, "submit_to_result_s": res["elapsed_s"],
                "oracle_or_circuits": res["oracle_calls"], "success_prob": 1.0,
                "note": res["note"],
            })

        # Aer (local) via IBM adapter (no token)
        if "aer" in args.modes:
            tag = f"{args.image_prefix}:{args.exp}-aer-n{n}"
            t0 = time.time()
            build_image(exp_file, tag, target="ibm", env_vars=params)
            build_s = time.time() - t0
            data = docker_run(tag, env={})  # no token

            top_dec, top_p, big_endian = parse_quantum_counts(data, n)
            rows.append({
                "exp": args.exp, "n": n, "backend": "aer_local",
                "build_s": round(build_s,3),
                "submit_to_result_s": data.get("elapsed_s"),
                "oracle_or_circuits": 1 if args.exp=="bv" else int((3.14159/4) * (2**(n/2))),  # Grover iteration estimate
                "success_prob": top_p,
                "note": f'solution_be={big_endian}',  # big-endian bitstring to compare to marked
            })

        # IBM Runtime simulator (needs token)
        if "ibm" in args.modes:
            token = os.getenv("IBM_TOKEN")
            if not token:
                print("[WARN] IBM mode requested but IBM_TOKEN not set; skipping.")
            else:
                tag = f"{args.image_prefix}:{args.exp}-ibm-n{n}"
                t0 = time.time()
                build_image(exp_file, tag, target="ibm", env_vars=params)
                build_s = time.time() - t0
                data = docker_run(tag, env={"IBM_TOKEN": token})
                top_dec, top_p, big_endian = parse_quantum_counts(data, n)
                rows.append({
                    "exp": args.exp, "n": n, "backend": "aer_local",
                    "build_s": round(build_s,3),
                    "submit_to_result_s": data.get("elapsed_s"),
                    "oracle_or_circuits": 1 if args.exp=="bv" else int((3.14159/4) * (2**(n/2))),  # Grover iteration estimate
                    "success_prob": top_p,
                    "note": f'solution_be={big_endian}',  # big-endian bitstring to compare to marked
                })

    with open(args.csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=[
            "exp","n","backend","build_s","submit_to_result_s","oracle_or_circuits","success_prob","note"
        ])
        w.writeheader(); w.writerows(rows)
    print("Wrote", args.csv)

if __name__ == "__main__":
    main()


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

def parse_quantum_counts(data, n):
    # data like {"counts": {"22956": 0.999..., ...}}
    counts = data.get("counts") or {}
    if not counts:
        return None, None, None
    # top outcome (decimal) and prob
    top_dec, top_p = max(((int(k), v) for k, v in counts.items()), key=lambda kv: kv[1])
    # to bitstring (little-endian in Qiskit’s readout)
    b = format(top_dec, f"0{n}b")
    # flip to big-endian to compare with our 'marked'
    big_endian = b[::-1]
    return top_dec, top_p, big_endian