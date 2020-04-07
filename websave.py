import sys
import os
import csv
import time
import urllib
import errno
from urllib.request import urlopen
from urllib.parse import quote
from datetime import datetime
import argparse
import ssl

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

def get_urls(csv_fname):
    l = []
    with open(csv_fname, newline="") as csvfile:
        r = csv.reader(csvfile)
        for row in r:
            if len(row) == 3:
                l.append((row[0], row[1], row[2]))
    return l

def save_webpage(url, fname):
    try:
        # Read the page
        s = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        req = urllib.request.Request(url, headers=headers)
        html = urlopen(url, context=s)
        page = html.read()
        # Save it
        os.makedirs(os.path.dirname(fname), exist_ok=True)
        with open(fname, "wb") as f:
            f.write(page)
        return True
    except:
        print("The URL {} could not be opened".format(url))
        return False

def save_all(csv_fname, folder, fails_csv):
    urls = get_urls(csv_fname)
    fails = []
    for university, category, u in urls:
        print("URL: {}".format(u))
        # Make the url safe for a filename
        f = quote(u, "")
        time = datetime.now()
        s = str(time)
        # Don't need milliseconds
        s = s.split(".")[0]
        # Underscore for slightly
        time_stamp = s.replace(" ", "_")
        time_stamp = time_stamp.replace(":", "-")
        #f = university + "_" + category + "_" + f + time_stamp + ".html"
        # Note: filenames may not be unique
        f = university + "_" + category + "_" + time_stamp + ".html"
        fname = os.path.join(folder, university, f)
        saved = save_webpage(u, fname)
        if not saved:
            fails.append((u,f))
    with open(fails_csv, "w", newline="") as csvfile:
        w = csv.writer(csvfile)
        for u,f in fails:
            w.writerow([u,f])

def save_all_loop(csv_fname, folder, period, fails):
    while True:
        print("Saving URLs")
        save_all(csv_fname, folder, fails)
        time.sleep(period)
        print("Done Saving")
        print("Waiting for {} seconds".format(period))

def get_args(arg_list):
    parser = argparse.ArgumentParser()
    parser.add_argument("--folder", metavar="<folder>", required=True, help="The path to the folder to save the .html files.")
    parser.add_argument("--csv", metavar="<filename>", required=True, help="The path to the csv file to read the URLs from.")
    parser.add_argument("--fails", metavar="<filename>", required=False, default="fails.csv")
    parser.add_argument("--period", metavar="n", required=False, const=86400, type=int, nargs="?", help="How often to save (in seconds). Defaults to 1 day = 86400 seconds")
    args = parser.parse_args(arg_list)
    return args

def main(arg_list):
    args = get_args(arg_list)
    # If periodic, then run the loop
    if args.period is not None:
        save_all_loop(args.csv, args.folder, args.period, args.fails)
    else:
        save_all(args.csv, args.folder, args.fails)

if __name__ == "__main__":
    main(sys.argv[1:])

