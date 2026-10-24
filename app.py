from flask import Flask, request, render_template_string
import socket
import requests
import ipaddress
app = Flask(__name__)
HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Domain Location Finder</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #eef2ff;
            text-align: center;
            padding: 40px 15px;
        }
        .box {
            background: white;
            max-width: 450px;
            margin: auto;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 4px 15px #ccd;
        }
        input, button {
            box-sizing: border-box;
            width: 100%;
            padding: 13px;
            margin-top: 12px;
            border-radius: 8px;
            font-size: 16px;
        }
        input {
            border: 1px solid #aaa;
        }
        button {
            background: #3344cc;
            color: white;
            border: none;
            cursor: pointer;
        }
        .result {
            text-align: left;
            background: #f2f5ff;
            padding: 15px;
            margin-top: 20px;
            border-radius: 8px;
            overflow-wrap: anywhere;
        }
        .error {
            color: #c00;
            margin-top: 15px;
        }
    </style>
</head>
<body>
    <div class="box">
        <h1>🌐 Domain Location Finder</h1>
        <p>Find a domain's IP address and approximate location.</p>
        <form method="POST">
            <input type="text" name="domain"
                   placeholder="Enter domain, e.g. google.com"
                   value="{{ domain }}" required>
            <button type="submit">Find Location</button>
        </form>
        {% if result %}
        <div class="result">
            <h3>Search Results</h3>
            <p><b>Domain:</b> {{ result.domain }}</p>
            <p><b>IP Address:</b> {{ result.ip }}</p>
            <p><b>City:</b> {{ result.city }}</p>
            <p><b>Region:</b> {{ result.region }}</p>
            <p><b>Country:</b> {{ result.country }}</p>
            <p><b>Coordinates:</b> {{ result.loc }}</p>
        </div>
        {% endif %}
        {% if error %}
        <p class="error">{{ error }}</p>
        {% endif %}
    </div>
</body>
</html>
"""
@app.route("/", methods=["GET", "POST"])
def home():
    result = None
    error = None
    domain = ""
    if request.method == "POST":
        domain = request.form.get("domain", "").strip()
        try:
            # Accept a domain name, not a URL or IP address.
            domain = domain.rstrip(".").lower()
            if (
                not domain
                or len(domain) > 253
                or any(c in domain for c in "/:@?#")
                or any(c.isspace() for c in domain)
            ):
                raise ValueError("Enter a valid domain, e.g. google.com")
            try:
                ipaddress.ip_address(domain)
                raise ValueError("Enter a domain name, not an IP address.")
            except ValueError as e:
                if str(e).startswith("Enter a domain"):
                    raise
            ip = socket.gethostbyname(domain)
            # Avoid querying location information for private IP addresses.
            if not ipaddress.ip_address(ip).is_global:
                raise ValueError("This domain resolved to a non-public IP.")
            response = requests.get(
                f"https://ipinfo.io/{ip}/json",
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            result = {
                "domain": domain,
                "ip": ip,
                "city": data.get("city", "Not available"),
                "region": data.get("region", "Not available"),
                "country": data.get("country", "Not available"),
                "loc": data.get("loc", "Not available")
            }
        except ValueError as e:
            error = str(e)
        except socket.gaierror:
            error = "Domain not found. Please check the spelling."
        except requests.RequestException:
            error = "Location service unavailable. Please try again."
        except Exception:
            error = "Something went wrong. Please try again."
    return render_template_string(
        HTML, result=result, error=error, domain=domain
    )
if __name__ == "__main__":
    app.run(debug=True)
