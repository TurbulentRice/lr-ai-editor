import argparse, sqlite3, csv, pathlib, shutil, json, os
from PIL import Image

def main():
  p = argparse.ArgumentParser()
  p.add_argument("--catalog")
  p.add_argument("--out_csv")
  p.add_argument("--previews_dir")
  args = p.parse_args()

  os.makedirs(args.previews_dir, exist_ok=True)

  conn = sqlite3.connect(args.catalog, uri=True)  # read-only
  cur = conn.cursor()

  cur.execute("""
    SELECT ag.images, ag.Exposure2012, ag.Contrast2012, ag.Shadows2012
    FROM AgDevelopSettings ag
    LIMIT 100
  """)

  with open(args.out_csv, "w", newline="") as f:
    wr = csv.writer(f)
    wr.writerow(["image", "exp", "contrast", "shadows"])
    for img_id, exp, con, sh in cur:
      wr.writerow([img_id, exp, con, sh])
  print("Dataset CSV written →", args.out_csv)

if __name__ == "__main__":
  main()