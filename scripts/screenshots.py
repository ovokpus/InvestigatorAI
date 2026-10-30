"""Capture README screenshots from the running stack (docker compose up first).

Run:  uv run --no-project --with playwright python scripts/screenshots.py
"""
from playwright.sync_api import sync_playwright

WEB, API, OUT = "http://localhost:3000", "http://localhost:8000", "docs/screenshots"

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1280, "height": 900}, color_scheme="dark")

    pg.goto(f"{WEB}/screening"); pg.wait_for_selector("text=Accuracy")
    pg.get_by_role("button", name="Screen transaction").click(); pg.wait_for_selector("text=risk score")
    pg.wait_for_timeout(500)
    pg.screenshot(path=f"{OUT}/screening-escalate.png", full_page=True)

    pg.get_by_role("button", name="Everyday grocery").click()
    pg.get_by_role("button", name="Screen transaction").click(); pg.wait_for_selector("text=approve")
    pg.wait_for_timeout(400)
    pg.locator("main").screenshot(path=f"{OUT}/screening-approve.png")

    pg.get_by_role("button", name="Late-night crypto abroad").click()
    pg.get_by_role("button", name="Screen transaction").click(); pg.wait_for_selector("text=Open full investigation")
    pg.get_by_text("Open full investigation").click(); pg.wait_for_load_state("networkidle"); pg.wait_for_timeout(1200)
    pg.screenshot(path=f"{OUT}/investigation-prefilled.png", full_page=True)

    pg.goto(f"{WEB}/tools"); pg.wait_for_load_state("networkidle"); pg.wait_for_timeout(800)
    pg.screenshot(path=f"{OUT}/tools.png")

    pg.goto(f"{API}/docs"); pg.wait_for_selector(".opblock"); pg.wait_for_timeout(500)
    pg.screenshot(path=f"{OUT}/api-docs.png", full_page=True)
    b.close()
