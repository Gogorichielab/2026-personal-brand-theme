---
title: "A Small CSS Cleanup"
date: 2026-05-01T09:00:00-05:00
tags: ["web","projects"]
lead: "A short maintenance session made a stylesheet easier to understand."
---

A short maintenance session made a stylesheet easier to understand.

I set aside half an hour to clean up a small stylesheet. The aim was to make the next change easier, so I started by reading rather than deleting.

Two spacing values appeared throughout the file. Giving them names made their relationship visible:

```css
:root {
  --space-small: 0.75rem;
  --space-large: 2rem;
}
```

## Check the edges

After the change, I checked a narrow screen, a long heading, and keyboard focus. Tidier CSS is only useful if the page still behaves well.

I stopped when the time was up and wrote down the next question. Small maintenance sessions are easier to repeat when they have a clear end.

