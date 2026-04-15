import { expect, test } from "@playwright/test";

test.describe("Marketing site", () => {
  test("landing page renders and shows lead form", async ({ page }) => {
    await page.goto("/");
    await expect(page).toHaveTitle(/Operra/i);
    // Primary CTA
    await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
    // Lead capture form anchor
    await page.locator("#demo").scrollIntoViewIfNeeded();
    await expect(page.getByRole("textbox", { name: /email/i })).toBeVisible();
  });

  test("sign-in route is reachable", async ({ page }) => {
    const response = await page.goto("/sign-in");
    expect(response?.status() ?? 200).toBeLessThan(500);
  });
});
