
import os
import stat

def check_env_var(var_name):
    path = os.environ.get(var_name)
    print(f"\nChecking {var_name}...")
    if not path:
        print(f"✖ {var_name} is not set.")
        return

    print(f"{var_name} is set to: {path}")

    # Check if file exists
    if not os.path.exists(path):
        print("✖ File does not exist at the given path.")
        print("Suggestion: Unset the variable or set it to a valid CA bundle path.")
        return
    else:
        print("✔ File exists.")

    # Check readability
    readable = os.access(path, os.R_OK)
    print(f"✔ Readable by user: {readable}")
    if not readable:
        print("Suggestion: Fix file permissions (chmod or chown).")

    # Check if it's a symlink
    if os.path.islink(path):
        print(f"✔ It is a symlink → points to: {os.readlink(path)}")
    else:
        print("✔ It is not a symlink.")

    # Check if file contains PEM certificates
    try:
        with open(path, "r", errors="ignore") as f:
            content = f.read()
            if "-----BEGIN CERTIFICATE-----" in content:
                print("✔ File contains PEM-encoded certificates.")
            else:
                print("✖ File does NOT contain PEM certificates. It may be in wrong format or corrupted.")
                print("Suggestion: Use a valid PEM CA bundle or install certifi and set REQUESTS_CA_BUNDLE to certifi.where().")
    except Exception as e:
        print(f"✖ Could not read file: {e}")

# Check both environment variables
check_env_var("SSL_CERT_FILE")
check_env_var("REQUESTS_CA_BUNDLE")

print("\nDiagnostics complete. If issues persist, consider using certifi:")
print("pip install certifi")
print("export REQUESTS_CA_BUNDLE=$(python -c \"import certifi; print(certifi.where())\")")
