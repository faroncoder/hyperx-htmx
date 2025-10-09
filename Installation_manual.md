Command	Purpose
---

`sudo python3 core_install_hyperx.py --system-install`	normal system install
`sudo python3 core_install_hyperx.py --system-install --report` 	install + export audit JSON to /var/log/hyperx_audit.json
`sudo python3 core_install_hyperx.py --system-install --report ./audit.json`	export audit to current dir
`python3 core_install_hyperx.py /path/to/settings.py --report ./dev_audit.json` 	developer-level audit export