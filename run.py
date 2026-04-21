# SPDX-License-Identifier: GPL-2.0-only
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
