from hyperx.bin.cli.logger.hx_logger import *
_logger = load_logger("jsx_runtime_parser")
_logger.info("jsx_runtime_parser initialized")


from pathlib import Path
import sys, re, shutil, os
from playwright.sync_api import sync_playwright

def location_route_file_reactjs(path: Path):
    """
    Given a file path, determine if it's a React route file based on common conventions.
    """
    routejsreact = []
    route_patterns = [
        r"src/routes/.*\.jsx?$",
        r"src/pages/.*\.jsx?$",
        r"src/components/.*Route.*\.jsx?$",
        r"src/App\.jsx?$",
        r"src/index\.jsx?$"
    ]
    for pattern in route_patterns:
        if re.search(pattern, Path):
            routejsreact.append(Path)
    return routejsreact


def is_react_project(base_path):  
    if not os.path.isdir(base_path):
        print(f"❌ The path {base_path} is not a valid directory.")
        base_path_ask = input("Where is the project root? ")

        if True:
            base_path = base_path_ask
            return is_react_project(base_path)
        else:
            sys.exit(1)
            
            
            
            # base_path = os.path.dirname(base_path)
            # base_path_ask = input("Where is the project root? ") or base_path
            # if not os.path.isdir(base_path_ask):
            #     print(f"❌ The path {base_path_ask} is not a valid directory.")
            #     return False and exit(1)
            # base_path = base_path_ask

        print(f"ℹ️ Using {base_path} as the project root.")
        return base_path


def scan_for_routes(base_path):
    route_files = []
    route_urls = []
    react_indicators = ["package.json", "src/App.js", "src/index.js", "src/App.jsx", "src/index.jsx"]
    for indicator in react_indicators:
        if os.path.exists(os.path.join(base_path, indicator)):
            base_dir = os.environ["REACTJS"] = base_path          
            print(f"ℹ️ Using {base_dir} as the React project root.")
            continue
        else:
            print(f"❌ No React indicators found in {base_path}. Not a React project?")
            sys.exit(1)
    for route in react_indicators:
        if os.path.exists(os.path.join(base_path, route)):
            extract_routes = location_route_file_reactjs(os.path.join(base_path, route))
            if extract_routes:
                route_files.extend(extract_routes)
                route_urls.extend([f"/{os.path.relpath(f, base_path)}" for f in extract_routes])
    if not route_files:
        print(f"❌ No route files found in {base_path}.")
        return False

    return route_urls



def capture_dom(route_urls):
    all_html = {}
    for route in route_urls:
        snapshots = crawl_localhost([route])
        for url, html in snapshots.items():
            print(f"📄 Capturing {url}")
            all_html[url] = html
    return all_html



def crawl_localhost(route_urls, max_depth=None):
    visited = set()
    to_visit = route_urls[:]
    snapshots = {}
    base = route_urls[0].split("/", 3)[0] + "//" + route_urls[0].split("/", 3)[2]  # e.g., http://localhost:3000
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        while to_visit:
            route = to_visit.pop()
            if route in visited or not route.startswith(base):
                continue
            visited.add(route)
            print(f"📄 Capturing {route}")
            page.goto(route)
            page.wait_for_timeout(1500)
            html = page.content()
            snapshots[route] = html

            # discover internal links
            links = page.eval_on_selector_all("a[href]", "els => els.map(e => e.getAttribute('href'))")
            for link in links:
                if link and link.startswith("/") and not link.startswith("//"):
                    full = f"{base.rstrip('/')}{link}"
                    if full not in visited and full not in to_visit:
                        to_visit.append(full)
        browser.close()
    return snapshots


    


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python runtime_parser.py <url>")
        sys.exit(1)
    url = sys.argv[1]
    dom_html = capture_dom(url)
    print(dom_html)
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python runtime_parser.py <project_root>")
        sys.exit(1)
    base_path = sys.argv[1]
    route_urls = scan_for_routes(base_path)
    if route_urls:
        dom_html = capture_dom(route_urls)
        print(dom_html)
