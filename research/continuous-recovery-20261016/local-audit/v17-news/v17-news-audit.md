# v17 News marker audit

Read-only comparison of the same 40 pages used by the accepted all-news audit.

- v16 valid image markers: **954**; v17: **798**; removed: **156**.
- Accepted new assets: **20**; ALLNEWS01 disappeared occurrences: **152 / 152 expected**; NEWS03+NEWS04: **4**.
- Unique requested URLs: v16 **636**, v17 **616**; no new valid marker URL appeared.
- v17 guide provenance reports **19** previews on **5** gallery pages; these cards are excluded from this News marker/download count.

## Per-page comparison

| route | v16 valid | v17 valid | delta | new-asset removals |
|---|---:|---:|---:|---:|
| `/index.xml` | 0 | 0 | 0 | 0 |
| `/info/archivednews.html` | 0 | 0 | 0 | 0 |
| `/news/rss-01-2007.xml` | 17 | 13 | 4 | 4 |
| `/news/rss-01-2008.xml` | 18 | 18 | 0 | 0 |
| `/news/rss-02-2007.xml` | 12 | 10 | 2 | 2 |
| `/news/rss-02-2008.xml` | 29 | 27 | 2 | 2 |
| `/news/rss-03-2007.xml` | 13 | 5 | 8 | 8 |
| `/news/rss-03-2008.xml` | 19 | 19 | 0 | 0 |
| `/news/rss-04-2007.xml` | 10 | 9 | 1 | 1 |
| `/news/rss-04-2008.xml` | 3 | 3 | 0 | 0 |
| `/news/rss-05-2007.xml` | 20 | 18 | 2 | 2 |
| `/news/rss-05-2008.xml` | 4 | 4 | 0 | 0 |
| `/news/rss-06-2007.xml` | 36 | 36 | 0 | 0 |
| `/news/rss-07-2006.xml` | 33 | 14 | 19 | 19 |
| `/news/rss-07-2007.xml` | 20 | 20 | 0 | 0 |
| `/news/rss-08-2006.xml` | 45 | 27 | 18 | 18 |
| `/news/rss-08-2007.xml` | 30 | 30 | 0 | 0 |
| `/news/rss-09-2006.xml` | 49 | 24 | 25 | 25 |
| `/news/rss-09-2007.xml` | 20 | 20 | 0 | 0 |
| `/news/rss-10-2006.xml` | 73 | 44 | 29 | 29 |
| `/news/rss-10-2007.xml` | 33 | 33 | 0 | 0 |
| `/news/rss-11-2006.xml` | 65 | 36 | 29 | 29 |
| `/news/rss-11-2007.xml` | 27 | 27 | 0 | 0 |
| `/news/rss-12-2006.xml` | 34 | 20 | 14 | 14 |
| `/news/rss-12-2007.xml` | 18 | 17 | 1 | 1 |
| `/news/wow-news-01-2006.html` | 0 | 0 | 0 | 0 |
| `/news/wow-news-02-2006.html` | 0 | 0 | 0 | 0 |
| `/news/wow-news-03-2006.html` | 0 | 0 | 0 | 0 |
| `/news/wow-news-04-2006.html` | 0 | 0 | 0 | 0 |
| `/news/wow-news-05-2006.html` | 0 | 0 | 0 | 0 |
| `/news/wow-news-06-2005.html` | 16 | 16 | 0 | 0 |
| `/news/wow-news-06-2006.html` | 0 | 0 | 0 | 0 |
| `/news/wow-news-07-2005.html` | 16 | 16 | 0 | 0 |
| `/news/wow-news-08-2005.html` | 15 | 15 | 0 | 0 |
| `/news/wow-news-09-2005.html` | 20 | 20 | 0 | 0 |
| `/news/wow-news-10-2005.html` | 12 | 12 | 0 | 0 |
| `/news/wow-news-11-2005.html` | 8 | 8 | 0 | 0 |
| `/news/wow-news-12-2005.html` | 0 | 0 | 0 | 0 |
| `/news/wow-news2004.html` | 166 | 164 | 2 | 2 |
| `/news/wow-news2005.html` | 73 | 73 | 0 | 0 |

## Twenty accepted URLs

| batch | URL | v16 occurrences | v17 occurrences | pages with v16 markers |
|---|---|---:|---:|---|
| allnews01 | `http://www.worldofwarcraft.com/new-hp/images/smallcaps/h.gif` | 52 | 0 | /news/rss-07-2006.xml, /news/rss-08-2006.xml, /news/rss-09-2006.xml, /news/rss-10-2006.xml, /news/rss-11-2006.xml, /news/rss-12-2006.xml |
| allnews01 | `http://www.worldofwarcraft.com/new-hp/images/smallcaps/a.gif` | 30 | 0 | /news/rss-01-2007.xml, /news/rss-02-2007.xml, /news/rss-02-2008.xml, /news/rss-03-2007.xml, /news/rss-04-2007.xml, /news/rss-05-2007.xml, /news/rss-07-2006.xml, /news/rss-08-2006.xml, /news/rss-09-2006.xml, /news/rss-10-2006.xml, /news/rss-11-2006.xml, /news/rss-12-2006.xml, /news/rss-12-2007.xml |
| allnews01 | `http://www.worldofwarcraft.com/new-hp/images/smallcaps/t.gif` | 29 | 0 | /news/rss-07-2006.xml, /news/rss-08-2006.xml, /news/rss-09-2006.xml, /news/rss-10-2006.xml, /news/rss-11-2006.xml, /news/rss-12-2006.xml |
| allnews01 | `http://www.worldofwarcraft.com/new-hp/images/smallcaps/d.gif` | 8 | 0 | /news/rss-09-2006.xml, /news/rss-10-2006.xml, /news/rss-11-2006.xml, /news/rss-12-2006.xml |
| allnews01 | `http://www.worldofwarcraft.com/new-hp/images/smallcaps/b.gif` | 5 | 0 | /news/rss-07-2006.xml, /news/rss-09-2006.xml, /news/rss-10-2006.xml, /news/rss-11-2006.xml |
| allnews01 | `http://www.worldofwarcraft.com/new-hp/images/smallcaps/o.gif` | 5 | 0 | /news/rss-07-2006.xml, /news/rss-09-2006.xml, /news/rss-10-2006.xml, /news/rss-12-2006.xml |
| allnews01 | `http://www.worldofwarcraft.com/new-hp/images/smallcaps/c.gif` | 3 | 0 | /news/rss-08-2006.xml, /news/rss-11-2006.xml |
| allnews01 | `http://www.worldofwarcraft.com/new-hp/images/smallcaps/e.gif` | 2 | 0 | /news/rss-09-2006.xml, /news/rss-11-2006.xml |
| allnews01 | `http://www.worldofwarcraft.com/new-hp/images/smallcaps/f.gif` | 2 | 0 | /news/rss-08-2006.xml, /news/rss-11-2006.xml |
| allnews01 | `http://www.worldofwarcraft.com/new-hp/images/smallcaps/s.gif` | 2 | 0 | /news/rss-08-2006.xml, /news/rss-11-2006.xml |
| allnews01 | `http://www.worldofwarcraft.com/new-hp/images/smallcaps/g.gif` | 1 | 0 | /news/rss-09-2006.xml |
| allnews01 | `http://www.worldofwarcraft.com/new-hp/images/smallcaps/j.gif` | 1 | 0 | /news/rss-09-2006.xml |
| allnews01 | `http://www.worldofwarcraft.com/new-hp/images/smallcaps/n.gif` | 1 | 0 | /news/rss-07-2006.xml |
| allnews01 | `http://www.worldofwarcraft.com/new-hp/images/smallcaps/v.gif` | 1 | 0 | /news/rss-07-2006.xml |
| allnews01 | `http://www.worldofwarcraft.com/news/images/07-02/ipod.jpg` | 8 | 0 | /news/rss-02-2007.xml, /news/rss-03-2007.xml |
| allnews01 | `http://www.worldofwarcraft.com/news/images/04-11/stressedorc.jpg` | 2 | 0 | /news/wow-news2004.html |
| news03 | `http://www.worldofwarcraft.com/news/images/07-01/1-18-07-4.gif` | 1 | 0 | /news/rss-01-2007.xml |
| news03 | `http://www.worldofwarcraft.com/news/images/07-01/1-25-07-1.jpg` | 1 | 0 | /news/rss-01-2007.xml |
| news04 | `http://www.worldofwarcraft.com/news/images/06-07/thumb-rogue.jpg` | 1 | 0 | /news/rss-07-2006.xml |
| news04 | `http://www.worldofwarcraft.com/news/images/07-01/1-25-07-2.jpg` | 1 | 0 | /news/rss-01-2007.xml |

The JSON receipt retains exact page/line locations and all locked input hashes. No network, build, production, or frozen-source writes were performed.
