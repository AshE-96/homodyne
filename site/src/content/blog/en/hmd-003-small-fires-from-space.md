---
title: "Can satellites spot a small forest fire from space?"
description: "Partly. VIIRS flags hot 375 m pixels, but each one is a lead, not a verdict. How to read NASA FIRMS data, using Iran's Elit forest fire as the case."
lang: en
translationKey: hmd-003-companion
hmd: HMD-003
kind: companion
date: 2026-12-04
tags: ["wildfire", "remote sensing", "VIIRS", "NASA FIRMS", "Hyrcanian forest", "FireSat"]
sources:
  - title: "NASA FIRMS (Fire Information for Resource Management System)"
    url: "https://firms.modaps.eosdis.nasa.gov/"
  - title: "NASA MODAPS · VNP14IMGTDL_NRT product page (VIIRS 375 m active fire)"
    url: "https://modaps.modaps.eosdis.nasa.gov/services/about/products/viirs-land-c2-nrt/vnp14imgtdl_nrt.html"
  - title: "NASA FIRMS · Fire Alerts: Important Notes"
    url: "https://firms.modaps.eosdis.nasa.gov/alerts/notes.php"
  - title: "Earth Fire Alliance & Muon Space · First light and first active fire images from operational FireSat (16 Sep 2026)"
    url: "https://earthfirealliance.org/news-article/earth-fire-alliance-and-muon-space-release-first-light-and-first-active-fire-images-from-operational-firesat-constellation/"
  - title: "Google · A breakthrough in wildfire detection (16 Sep 2024)"
    url: "https://blog.google/outreach-initiatives/sustainability/google-ai-wildfire-detection/"
  - title: "Iran International · Hyrcanian forest fires (17 Nov 2025)"
    url: "https://www.iranintl.com/en/202511174535"
  - title: "Iran International (Persian) · Elit forest fire report (27 Nov 2025)"
    url: "https://www.iranintl.com/fa/202511276713"
  - title: "IQAir · Wildfire Map Spotlight: Hyrcanian Forest Fire, Iran"
    url: "https://www.iqair.com/newsroom/wildfire-map-spotlight-hyrcanian-forest-fire-iran"
---

Yes, increasingly, but not yet everywhere or every hour. Satellites built specifically for fire can, according to their operators, detect fires as small as 5 by 5 metres. What anyone can download for northern Iran today, for free, is VIIRS hot-spot data from NASA's FIRMS service, and each of those dots is a lead, not a verdict.

> **Key Takeaways**
> - A VIIRS hot spot means "somewhere in a roughly 14-hectare square, at the moment the satellite passed, it was hotter than its surroundings". It does not have to be a forest fire.
> - Factories, gas flares and sun glint also produce hot spots. Two simple checks (near a known industrial site, hot on several days) help, and both can be wrong.
> - A stricter confidence threshold removes false alarms and also removes the earliest faint signs of real fires.
> - Official burned-area estimates for Iran's Elit fire range from about 8 ha to 150 to 180 ha. The FIRMS timeline for that fire has not been run yet.
> - Without a reliable ground-truth list, nobody can state a precision or recall.

## What does a satellite actually see?

A satellite does not photograph flames. It records heat in infrared wavelengths. Its image is a grid of pixels, and when one pixel is clearly hotter than its neighbours, the detection algorithm marks a "hot spot".

For the VIIRS instrument each pixel is about 375 by 375 metres. The arithmetic: 375 × 375 = 140,625 square metres, about 14 hectares or roughly twenty football pitches. The older MODIS instrument works with pixels of about 1 km, and NASA's [FIRMS notes](https://firms.modaps.eosdis.nasa.gov/alerts/notes.php) say VIIRS responds better to small fires.

Pixel size is not the smallest detectable fire. A small but very hot fire can light up a whole pixel; you just no longer know where in those 14 hectares it is. NASA's [VIIRS product page](https://modaps.modaps.eosdis.nasa.gov/services/about/products/viirs-land-c2-nrt/vnp14imgtdl_nrt.html) defines each row's coordinates as the "center of nominal 375 m fire pixel", not the exact position of the fire.

Time is the other limit. These satellites are not overhead all the time; they look only when they pass. Each dot describes that moment, not the hours between passes.

## Is every hot spot a forest fire?

No. Anything that stays hot, such as a power plant, a factory or a gas flare, can look like a fire from orbit. Reflected light matters too: the same NASA page says low-confidence daytime pixels are "typically associated with areas of Sun glint".

The small Python script published with this episode checks two clues:

1. **Near an industrial site:** is the detection within a short distance (2 km by default) of a place you listed yourself?
2. **Recurring:** was the same spot, within 0.5 km, hot on three or more different days? Forest fires usually move; a chimney stays put.

FIRMS also has a `type` column that separates static land heat sources, but it exists only in the standard-processing (SP) product, not in the near-real-time (NRT) feed.

Both clues can mislead. A fire that starts right next to a factory gets flagged, and a fire that smoulders in one place for days can look "recurring". A flag means "look carefully", not "delete".

## What does the confidence threshold change?

VIIRS reports one of three confidence levels per detection: low, nominal or high. Picking a threshold is, in practice, picking between earlier warnings and false alarms.

We ran the script on an **ILLUSTRATIVE** sample: 18 synthetic rows written to teach the columns, not downloaded from FIRMS and not describing any real fire. Using the wider Mazandaran box (`--region mazandaran`), on that sample:

- At "low", all 18 detections are kept; at "nominal", 15; at "high", only 7.
- The first kept detection is not a fire at all. It sits next to the made-up industrial site SITE-A and recurs on all five days of the sample.
- At "low", a faint detection appears at the future fire's location about 12 hours before the first nominal detection there. Another faint daytime detection also appears that has nothing to do with the fire.

No threshold is right for everyone. The right one depends on how much more a missed fire costs you than a false alarm. [HMD-002](/en/episodes/hmd-002/) showed the same trade-off in AI scoreboards: a wrong answer versus "I don't know".

## What do we know, and not know, about the Elit fire?

The Elit forest fire, near Marzanabad in Chalus County, Mazandaran province (northern Iran, on the Caspian side of the Alborz mountains), started on 10 Aban 1404 (1 November 2025) according to reports and flared up again on 24 Aban (15 November). The area is part of the Hyrcanian forests, a UNESCO World Heritage site. Iran International described steep, rocky slopes, and IQAir reported that authorities confirmed full containment by 25 November 2025.

A simple question, "how much burned?", has no single official answer:

| Who said it | Burned-area estimate |
|---|---|
| Deputy agriculture minister and the provincial governor | about 8 ha |
| Natural Resources organisation | about 10 ha |
| Deputy head of the Department of Environment | 150 to 180 ha |

The largest and smallest estimates differ by roughly a factor of twenty (150 to 180 divided by 8 is about 19 to 22).

This is where satellite data helps: not because it is error-free, but because it looks the same way every time and is open to everyone. To be clear, though: **the FIRMS timeline for the Elit fire has not been run yet.** No number from it appears in this post or in the video. Running it needs only a free FIRMS key (a MAP_KEY), and the full commands are in the [technical deep dive](/en/blog/hmd-003-firms-methods/) so you can run it yourself.

When you do see that timeline, read it as "what the satellite saw when it passed", not "what happened on the ground", and not "the first moment of the fire".

## Why is there no accuracy figure without ground truth?

To say what share of alerts were real fires (precision) or what share of fires were detected (recall), you need a trustworthy list from the ground: where, when, how much burned. We have no such list for northern Iran, so we report no accuracy percentage for VIIRS there. The script deliberately prints none.

FIRMS itself lists reasons a fire can be missed: it started and ended between satellite overpasses, or it was hidden by cloud, heavy smoke or tree canopy. In dense Hyrcanian forest the last one is serious; a fire creeping under the canopy can look much weaker from above than it is. No dot does not mean no fire.

## What do FireSat and AI change?

On 16 September 2026, Earth Fire Alliance and Muon Space released the first active-fire images from the operational FireSat constellation: three satellites that reached orbit on 7 July 2026. According to them, the infrared sensors can see fires down to 5 by 5 metres, about two parking spaces. One example was a grass fire on the Oregon and Idaho border, seen five times over three nights and two days.

Their own roadmap: operational data at least twice a day to early adopters by the end of 2026, global access in 2028, hourly revisits in 2029, and every 20 minutes in the early 2030s. "Every twenty minutes" is the goal for the full constellation, not today's capability. And spotting a fire is not putting it out; an early alert is worth something only if someone can reach that slope quickly.

Google, a partner in the project, described the role of AI in 2024: rapidly comparing any 5 by 5 metre spot with previous imagery of the same place, alongside nearby infrastructure and local weather. Our script's two clues ("was it hot before?" and "is there a factory nearby?") are a transparent, hand-built version of two of those questions. The script is not FireSat and does not reproduce Google's model.

## What this does not show

- Our map and script use VIIRS data from FIRMS, not FireSat.
- Not every hot spot is a forest fire, and not every "non-fire" flag is right.
- We do not know how accurate VIIRS is in northern Iran; that needs ground truth.
- We do not claim a satellite saw the Elit fire before people on the ground did; its timeline has not been run.
- We do not claim FireSat is operating over Iran today.
- The 18, 15 and 7 come from ILLUSTRATIVE data and say nothing about any real fire.

## Where to go next

- The video and deck: [HMD-003 episode page](/en/episodes/hmd-003/)
- Datasets, columns and the commands to run FIRMS yourself: [HMD-003 deep dive](/en/blog/hmd-003-firms-methods/)
- Next episode, on why a correct diagnosis depends on the metric: [HMD-004](/en/episodes/hmd-004/)
- Persian original: [آیا می‌توان آتش کوچک جنگل را از فضا دید؟](/fa/blog/hmd-003-small-fires-from-space/)
