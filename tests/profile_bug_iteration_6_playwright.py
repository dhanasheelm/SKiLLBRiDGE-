"""Standalone focused Playwright test for iteration 6 /profile bug verification."""

import asyncio

from playwright.async_api import async_playwright


BASE = "https://ai-match-hub-10.preview.emergentagent.com"


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1920, "height": 1080})
        console_errors = []
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
        page.on("pageerror", lambda exc: console_errors.append(f"PAGEERROR: {exc}"))

        await page.goto(BASE, wait_until="domcontentloaded")
        await page.evaluate("localStorage.clear()")
        await page.goto(f"{BASE}/student/login", wait_until="domcontentloaded")
        async with page.expect_response(lambda r: "/api/users" in r.url and r.request.method == "POST"):
            await page.get_by_test_id("demo-access-button").click()
        await page.wait_for_url("**/home")
        assert await page.get_by_test_id("home-match-score").inner_text()

        await page.get_by_test_id("profile-menu-button").click()
        await page.wait_for_url("**/profile")
        await page.wait_for_selector('[data-testid="profile-page"]')
        profile_text = await page.get_by_test_id("profile-page").inner_text()
        assert "Find opportunities" not in profile_text and "that fit you" not in profile_text
        for testid in [
            "profile-initials", "profile-name", "profile-role", "profile-email", "profile-completion-bar",
            "profile-completion", "profile-fact-email", "profile-fact-role", "profile-goal",
            "profile-skills", "profile-interests",
        ]:
            await page.wait_for_selector(f'[data-testid="{testid}"]')
        assert (await page.get_by_test_id("profile-name").inner_text()).strip() == "Aarav Mehta"
        assert "aarav@demo.com" in await page.get_by_test_id("profile-email").inner_text()
        assert (await page.get_by_test_id("profile-role").inner_text()).strip() == "STUDENT PROFILE"
        assert (await page.get_by_test_id("profile-fact-role").inner_text()).strip() == "Student"

        await page.get_by_test_id("edit-profile-button").click()
        await page.wait_for_selector('[data-testid="edit-profile-modal"]')
        for testid in [
            "edit-name-input", "edit-email-input", "edit-college-input", "edit-degree-input",
            "edit-location-input", "edit-goal-input", "edit-new-skill-input", "edit-add-skill-button",
            "edit-new-interest-input", "edit-add-interest-button",
        ]:
            await page.wait_for_selector(f'[data-testid="{testid}"]')
        await page.get_by_test_id("edit-email-input").fill("invalid-email")
        await page.get_by_test_id("edit-profile-save").click()
        await page.wait_for_selector('[data-testid="edit-profile-error"]')

        await page.get_by_test_id("edit-name-input").fill("Aarav Iteration Six")
        await page.get_by_test_id("edit-email-input").fill("aarav.iteration6@example.com")
        await page.get_by_test_id("edit-college-input").fill("VIT QA College")
        await page.get_by_test_id("edit-degree-input").fill("B.Tech QA Focus")
        await page.get_by_test_id("edit-location-input").fill("Pune, India")
        await page.get_by_test_id("edit-goal-input").fill("AI Product Engineer")
        await page.get_by_test_id("edit-new-skill-input").fill("GraphQL")
        await page.get_by_test_id("edit-add-skill-button").click()
        await page.get_by_test_id("edit-new-interest-input").fill("Open Source")
        await page.get_by_test_id("edit-add-interest-button").click()
        async with page.expect_response(lambda r: "/api/users" in r.url and r.request.method == "POST") as save_info:
            await page.get_by_test_id("edit-profile-save").click()
        assert (await save_info.value).status == 200
        await page.wait_for_selector('[data-testid="edit-profile-modal"]', state="detached")
        assert (await page.get_by_test_id("profile-name").inner_text()).strip() == "Aarav Iteration Six"
        assert (await page.get_by_test_id("profile-fact-email").inner_text()).strip() == "aarav.iteration6@example.com"
        assert (await page.get_by_test_id("profile-goal").inner_text()).strip() == "AI Product Engineer"
        await page.wait_for_selector('[data-testid="profile-skill-graphql"]')
        await page.wait_for_selector('[data-testid="profile-interest-open-source"]')

        stored = await page.evaluate("JSON.parse(localStorage.getItem('skillbridge_user'))")
        assert stored["email"] == "aarav.iteration6@example.com"
        await page.reload(wait_until="domcontentloaded")
        await page.wait_for_selector('[data-testid="profile-page"]')
        assert (await page.get_by_test_id("profile-name").inner_text()).strip() == "Aarav Iteration Six"

        await page.get_by_test_id("nav-dashboard-link").click()
        await page.wait_for_selector('[data-testid="dashboard-match"]')
        assert await page.locator(".skill-line").count() >= 1
        await page.get_by_test_id("nav-opportunities-link").click()
        await page.wait_for_selector('[data-testid="opportunities-count"]')
        await page.get_by_test_id("nav-my-applications-link").click()
        await page.wait_for_selector('[data-testid="applications-empty"], [data-testid="applications-list"], [data-testid="applications-loading"]')

        await page.get_by_test_id("logout-button").click()
        await page.goto(f"{BASE}/professional/login", wait_until="domcontentloaded")
        await page.get_by_test_id("demo-access-button").click()
        await page.wait_for_selector('[data-testid="nav-workspace-link"]')
        await page.get_by_test_id("nav-workspace-link").click()
        await page.wait_for_selector('[data-testid="workspace-match"]')
        assert not console_errors, console_errors
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())