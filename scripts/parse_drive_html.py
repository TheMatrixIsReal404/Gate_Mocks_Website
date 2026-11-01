import re
import json

with open('drive_page.html', encoding='utf-8') as f:
    html = f.read()

# Google Drive folder pages often have _DRIVE_BOOTSTRAP_DATA or window['_data'] or similar JSON blobs
print("Checking for patterns...")

# Look for filename extensions or IDs
matches = re.findall(r'(\b[a-zA-Z0-9_\-\. ]+\.(?:pdf|json|zip|txt|csv|xlsx|docx))\b', html, re.IGNORECASE)
print(f"File-like names found ({len(matches)}):", list(set(matches))[:20] if matches else "None")

# Look for drive file IDs
# In drive HTML, items often look like: ["file_id","File Name.ext",...]
items = re.findall(r'\["([a-zA-Z0-9_-]{28,})","([^"]+)"', html)
print(f"ID-Name pairs ({len(items)}):")
for i, name in items[:25]:
    print(f"  {i} -> {name}")

# Also look for data-id or jsmodel
# Let's search for "GATE" or subject names
gate_refs = re.findall(r'([^"\\]*GATE[^"\\]*)', html, re.IGNORECASE)
print(f"GATE references ({len(gate_refs)}):", list(set(gate_refs))[:15])
