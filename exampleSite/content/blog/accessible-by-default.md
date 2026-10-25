---
title: "Accessible by Default"
date: 2026-03-10T09:00:00-05:00
tags: ["accessibility", "notes"]
lead: "A longer post with headings, so the theme shows its table of contents."
---

Accessibility is easiest when it is the default rather than a fix applied at the end. This post walks through a few habits that make a personal site welcoming to more people. It is also long enough, with enough headings, that the theme adds an "In this article" table of contents at the top.

## Start with semantic HTML

The fastest way to an accessible page is to use the elements browsers already understand. Headings should describe the structure of the page, in order, without skipping levels just to get a smaller font. Lists should be lists. Buttons should be buttons, and links should go somewhere. When the markup says what something is, assistive technology can announce it correctly without any extra work.

Landmarks matter too. A page with a header, a main region, and a footer lets screen reader users jump straight to the content they came for. A "skip to content" link does the same for keyboard users, and this theme includes one at the very top of every page.

## Make focus visible

Keyboard users navigate by moving focus from one interactive element to the next. If they cannot see where focus is, the page is effectively unusable. Browsers provide a default focus ring, and the most common accessibility bug on the web is a stylesheet that removes it without offering a replacement.

A good focus style has strong contrast against the background, does not rely on color alone, and appears on every interactive element: links, buttons, form fields, and anything else that can receive focus. It is worth tabbing through your own site after every design change to make sure nothing has slipped.

## Write meaningful alternative text

Images that carry information need alternative text that conveys the same information. A chart needs a summary of what it shows. A photo of a crowded conference room might need a sentence about the scale of the event. Decorative images, on the other hand, should have empty alternative text so screen readers skip them entirely.

The best alternative text answers the question "what would I say about this image if I were describing the page over the phone?" It is usually shorter than you expect and rarely starts with "image of".

## Check color contrast

Text needs enough contrast against its background to be readable by people with low vision, in bright sunlight, or on a cheap screen. The Web Content Accessibility Guidelines recommend a contrast ratio of at least 4.5 to 1 for body text and 3 to 1 for large text. Many design tools now show contrast ratios directly, and browser developer tools can flag low-contrast text automatically.

Contrast applies to more than text. Form field borders, icons that carry meaning, and focus indicators all need to be distinguishable from their surroundings.

## Respect user preferences

Operating systems let people ask for reduced motion, larger text, and higher contrast. A considerate site listens. Animations can be shortened or removed when someone prefers reduced motion. Layouts should hold together when text is enlarged to two hundred percent. Sizes set in relative units make this much easier than fixed pixel values.

## Test with real tools

Automated checkers catch a useful share of problems, such as missing alternative text or low contrast, but not all of them. Spend a few minutes navigating your site with only a keyboard, then try a screen reader such as VoiceOver or NVDA. You will learn more in ten minutes of real use than in an hour of reading guidelines.

## Keep going

Accessibility is not a checklist you finish. Every new page and component is a chance to keep the defaults strong. Small, consistent habits add up to a site that more people can enjoy.
