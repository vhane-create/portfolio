# Credential verification QR codes

Each SVG encodes the exact official verification URL recorded in `credentials.json`. The portfolio serves the QR assets directly, without an external QR service. Expand **Scan verification QR** next to a credential to scan it. Existing clickable verification links remain available.

All 173 saved SVG codes were independently rasterized from their path geometry and decoded with ZXing; every decoded URL matched its credential record. Four-module quiet zones, black-on-white modules and medium error correction are included.
