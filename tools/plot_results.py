import sys, pandas as pd, matplotlib.pyplot as plt

def main(p):
    df = pd.read_csv(p)
    for backend in df['backend'].unique():
        sub = df[df['backend']==backend]
        plt.figure()
        plt.plot(sub['n'], sub['submit_to_result_s'], marker='o')
        plt.title(f"Submit→Result Time — {backend}")
        plt.xlabel("n")
        plt.ylabel("seconds")
        plt.grid(True)
        plt.show()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python tools/plot_results.py results.csv")
    else:
        main(sys.argv[1])
