import requests
import json
import argparse
import concurrent.futures
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich import print
import sys

def save_json(json_data,output):
    json.dump(json_data, open(output, "w"))

def send_request(username):
    headers = {
               "user-agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/111.0",
               }

    payload = '{ "username": "' + username +'", "language": "english"}'

    res = requests.post("https://github-roast.pages.dev/llama",
                        headers = headers,
                        data = payload
                        )

    json_data = json.loads(res.text)

    if res.status_code == 200:
        return json_data

def banner():
    print(r"""[purple]
                              __                
_______  _________    _______/  |_  ___________ 
[red]\_  __ \/  _ \__  \  /  ___/\   __\/ __ \_  __ \
 |  | \(  <_> ) __ \_\___ \  |  | \  ___/|  | \/
 [yellow]|__|   \____(____  /____  > |__|  \___  >__|   
      [green]            \/     \/            \/       
""")

def main():
    parser = argparse.ArgumentParser(description=".......")
    parser.add_argument("file", type=str, help="File with valid usernames")
    parser.add_argument("-t", "--threads", type=int, default=10, help="Number of threads to use")
    parser.add_argument("-o", "--output", type=str, default="output.json", help="Output file")
    args = parser.parse_args()
    usernames = [line.strip() for line in open(args.file, "r")]
    output = {}

          
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]Checking usernames..."),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TextColumn("[green]{task.completed}/{task.total}"),
        ) as progress:
            task = progress.add_task("", total=len(usernames))
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as executor:
                future_to_username = {executor.submit(send_request, username): username for username in usernames}
                for future in concurrent.futures.as_completed(future_to_username):
                    username = future_to_username[future]
                    try:
                        status = future.result()
                        if status:
                            print(f"[bold green]{status}[/bold green]")
                            output[username] = status
                        else:
                            print(f"[bold red]{username}[/bold red]")
                        progress.update(task, advance=1)
                    except Exception as e:
                        print(f"Error processing {username}: {e}")
    except KeyboardInterrupt:
        print("\n[bold red]Interrupted! Saving progress...[/bold red]")
        save_json(output, args.output)
        print(f"[bold yellow]Progress saved to {args.output}[/bold yellow]")
        sys.exit(1)

    save_json(output, args.output)
if __name__ == "__main__":
    banner()
    main()
