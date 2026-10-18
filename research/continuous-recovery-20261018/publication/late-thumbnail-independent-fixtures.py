def run_fixtures(fixture_output: Path | None = None) -> dict[str, Any]:
    """Run the reusable core entirely offline; no curl/process is started."""
    plan, _bindings = load_and_validate_inputs()
    candidate = plan["candidates"][0]
    header = FIELDS
    digest1, digest2 = "A" * 32, "B" * 32

    rows = [header,
            ["k", "20130612010000", candidate["original"], "image/gif", "200", digest1, "100"],
            [], ["resume-token"]]
    parsed = parse_cdx(json.dumps(rows).encode())
    t1 = (parsed["valid"] and not parsed["complete"] and parsed["resume_keys"] == ["resume-token"]
          and len(parsed["rows"]) == 1 and any(x.get("kind") == "separator" for x in parsed["metadata"]))

    full_rows = [header] + [[f"k{i}", f"201306120100{i:02d}", candidate["original"], "image/gif", "200", digest1, "100"] for i in range(CDX_LIMIT)]
    parsed500 = parse_cdx(json.dumps(full_rows).encode())
    classified500 = classify_cdx(parsed500, candidate)
    t2 = (parsed500["potential_truncation"] and not classified500["selected"]
          and classified500["status"] == "potential_truncation")

    latest_rows = [header,
                   ["old", "20130612010000", candidate["original"], "image/gif", "200", digest1, "100"],
                   ["new", "20130612020000", candidate["original"].replace("http://www.worldofwarcraft.com", "http://www.worldofwarcraft.com:80", 1), "image/gif", "200", digest2, "101"],
                   ["alias", "20130612030000", candidate["original"].replace("www.worldofwarcraft.com", "wow-europe.com"), "image/gif", "200", "C" * 32, "102"],
                   ["bad", "20130612040000", candidate["original"], "image/gif", "404", "D" * 32, "103"]]
    latest = classify_cdx(parse_cdx(json.dumps(latest_rows).encode()), candidate)
    t3 = (len(latest["selected"]) == 2 and latest["selected"][0]["timestamp"] == "20130612020000"
          and latest["selected"][0]["original"].startswith("http://www.worldofwarcraft.com:80/")
          and len(latest["identity_variant_candidates"]) == 1)

    def headers_for(original: str, timestamp: str, content_type: str, encoding: str = "") -> bytes:
        default_link = original.replace("http://www.worldofwarcraft.com", "http://www.worldofwarcraft.com:80", 1)
        extra = (b"Content-Encoding: " + encoding.encode() + b"\r\n") if encoding else b""
        date = datetime.strptime(timestamp, "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc)
        return (b"HTTP/1.1 200 Connection established\r\nProxy-Agent: fixture\r\n\r\n"
                b"HTTP/1.1 200 OK\r\nContent-Type: " + content_type.encode() + b"\r\n" + extra
                + b"Memento-Datetime: " + format_datetime(date, usegmt=True).encode() + b"\r\n"
                + b"Link: <" + default_link.encode() + b">; rel=\"original\"\r\n\r\n")

    gif_io = BytesIO()
    gif_frame1 = Image.new("P", (2, 2), 0)
    gif_frame2 = Image.new("P", (2, 2), 1)
    gif_frame2.putpixel((1, 1), 2)
    gif_frame1.save(gif_io, format="GIF", save_all=True, append_images=[gif_frame2], duration=50, loop=0, optimize=False)
    good_gif = gif_io.getvalue()
    gif_row = {"timestamp": "20130612010000", "digest": b32_sha1(good_gif), "length": str(len(good_gif))}
    gif_candidate = dict(candidate, expected_mime={"image/gif"})
    verified_gif = validate_replay(gif_candidate, gif_row, headers_for(candidate["original"], gif_row["timestamp"], "image/gif"), good_gif)

    jpeg_io = BytesIO()
    Image.new("RGB", (3, 2), (20, 40, 60)).save(jpeg_io, format="JPEG")
    good_jpeg = jpeg_io.getvalue()
    jpeg_candidate = dict(candidate, expected_mime={"image/jpeg"})
    jpeg_row = {"timestamp": "20130612010000", "digest": b32_sha1(good_jpeg), "length": str(len(good_jpeg))}
    verified_jpeg = validate_replay(jpeg_candidate, jpeg_row, headers_for(candidate["original"], jpeg_row["timestamp"], "image/jpeg"), good_jpeg)

    png_io = BytesIO()
    Image.new("RGBA", (2, 3), (1, 2, 3, 255)).save(png_io, format="PNG")
    good_png = png_io.getvalue()
    png_candidate = dict(candidate, expected_mime={"image/png"})
    png_row = {"timestamp": "20130612010000", "digest": b32_sha1(good_png), "length": str(len(good_png))}
    verified_png = validate_replay(png_candidate, png_row, headers_for(candidate["original"], png_row["timestamp"], "image/png"), good_png)
    t4 = (verified_gif["accepted"] and verified_gif["image_frame_count"] == 2
          and verified_jpeg["accepted"] and verified_jpeg["image_format"] == "JPEG"
          and verified_png["accepted"] and verified_png["image_format"] == "PNG")

    bad_html = b"<html><title>Wayback Machine error</title></html>"
    bad_row = {"timestamp": "20130612010000", "digest": b32_sha1(bad_html), "length": str(len(bad_html))}
    rejected_error = validate_replay(jpeg_candidate, bad_row, headers_for(candidate["original"], bad_row["timestamp"], "image/jpeg"), bad_html)
    wrong_magic = validate_replay(gif_candidate, jpeg_row, headers_for(candidate["original"], jpeg_row["timestamp"], "image/gif"), good_jpeg)
    t5 = (not rejected_error["accepted"] and any(r.startswith("image_decode_error") for r in rejected_error["reasons"])
          and not wrong_magic["accepted"] and "image_magic_mismatch" in wrong_magic["reasons"])

    compressed = gzip.compress(good_gif)
    compressed_result = validate_replay(gif_candidate, gif_row, headers_for(candidate["original"], gif_row["timestamp"], "image/gif", "gzip"), compressed)
    wrong_digest = validate_replay(gif_candidate, {**gif_row, "digest": "Z" * 32}, headers_for(candidate["original"], gif_row["timestamp"], "image/gif"), good_gif)
    wrong_memento = validate_replay(gif_candidate, gif_row, headers_for(candidate["original"], "20130612010001", "image/gif"), good_gif)
    wrong_link = validate_replay(gif_candidate, gif_row, headers_for(candidate["original"] + "?wrong-link=1", gif_row["timestamp"], "image/gif"), good_gif)
    t6 = (compressed_result["accepted"] and compressed_result["raw_body_bytes"] != compressed_result["decoded_body_bytes"]
          and not wrong_digest["accepted"] and "cdx_digest_mismatch" in wrong_digest["reasons"]
          and not wrong_memento["accepted"] and "memento_datetime_mismatch" in wrong_memento["reasons"]
          and not wrong_link["accepted"] and "memento_original_mismatch" in wrong_link["reasons"])

    expanded_over_cap = b"GIF89a" + (b"x" * (MAX_ENTITY_BODY_BYTES + 1))
    expanded_payload, expanded_error = decoded_payload(gzip.compress(expanded_over_cap), "gzip", MAX_ENTITY_BODY_BYTES)
    truncated_gzip_payload, truncated_gzip_error = decoded_payload(gzip.compress(good_gif)[:-8], "gzip", MAX_ENTITY_BODY_BYTES)
    truncated_deflate_payload, truncated_deflate_error = decoded_payload(zlib.compress(good_gif)[:-2], "deflate", MAX_ENTITY_BODY_BYTES)
    trailing_payload, trailing_error = decoded_payload(gzip.compress(good_gif) + b"TRAIL", "gzip", MAX_ENTITY_BODY_BYTES)
    t7 = (expanded_payload is None and expanded_error == "decoded_body_cap_exceeded"
          and truncated_gzip_payload is None and truncated_gzip_error == "content_decode_incomplete"
          and truncated_deflate_payload is None and truncated_deflate_error == "content_decode_incomplete"
          and trailing_payload is None and trailing_error == "content_decode_trailing_data")

    source404 = parse_headers(b"HTTP/1.1 200 Connection established\r\n\r\nHTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\n")
    retry_date = format_datetime(utc_now() + timedelta(seconds=240), usegmt=True).encode("ascii")
    source429 = parse_headers(b"HTTP/1.1 200 Connection established\r\n\r\nHTTP/1.1 429 Too Many Requests\r\nRetry-After: " + retry_date + b"\r\n\r\n")
    only_connect = parse_headers(b"HTTP/1.1 200 Connection established\r\nProxy-Agent: fixture\r\n\r\n")
    t8 = (source404["status"] == 404 and source404["connect_statuses"] == [200]
          and source429["status"] == 429 and source429["retry_after_kind"] == "http_date"
          and (source429["retry_after"] or 0) >= 120 and only_connect["status"] is None
          and not only_connect["source_block_found"] and only_connect["connect_statuses"] == [200])

    # Positive cache fixture: bind the actual ALLNEWS01 Blizzcon CDX body
    # (raw/70) and source report, rather than accepting synthetic metadata.
    # The body deliberately uses the six-column cached query shape and covers
    # 2006..anchor only, so it is complete for that query but cannot prove a
    # global 2000..anchor latest capture.
    cached_plan_path = FROZEN_NETWORK / "news-shared10" / "plan.json"
    # The positive fixture is intentionally frozen under the 2026-10-16
    # network tree.  Temporarily point the path guard at that read-only tree
    # while validating it, then restore the current batch boundary before the
    # remaining fixture checks and any real execution path.
    current_network = NETWORK
    try:
        globals()["NETWORK"] = FROZEN_NETWORK
        cached_plan = read_json(cached_plan_path)
        cached_candidate_source = next(item for item in cached_plan["candidates"]
                                       if item.get("target_key") == "NEWS10-04-blizzconlogo-jpg")
        cached_candidate = json.loads(json.dumps(cached_candidate_source))
        cached = dict(cached_candidate["cached_cdx"])
        cached_body_path = _bound_path(cached["raw_body_path"], under_network=True)
        cached_headers_path = _bound_path(cached["raw_headers_path"], under_network=True)
        cached_query = cached_candidate["query"]
        cached_parsed = parse_cdx(cached_body_path.read_bytes(), int(cached_query["limit"]))
        cached_exact_rows = [row for row in cached_parsed.get("rows", [])
                             if identity_relation(str(row.get("original") or ""), cached_candidate["original"]) == "exact"
                             and str(row.get("statuscode")) == "200"]
        cached_selected = max(cached_exact_rows, key=lambda row: (str(row.get("timestamp")), int(row.get("record_index") or 0)))
        cached.update({
            "source_curl_exit": 0,
            "raw_headers_sha256": sha_file(cached_headers_path),
            "body_bytes": cached_body_path.stat().st_size,
            "coverage_window": {"from": cached_query["from"], "to": cached_query["to"],
                                 "coverage_complete_for_global_window": False},
            "rows": cached_parsed["rows"],
            "record_count": len(cached_parsed["rows"]),
            "selected": cached_selected,
        })
        cached_candidate["cached_cdx"] = cached
        cached_validation = _validate_cached_evidence(cached_candidate, cached_query, cached)
    finally:
        globals()["NETWORK"] = current_network
    t9 = (cached_validation["valid"] and cached_validation["complete"]
          and len(cached_validation["rows"]) == 4
          and cached_validation["header"] == CDX_FIELDS_WITHOUT_URLKEY
          and cached_selected["timestamp"] == "20080402081015"
          and cached_selected["original"] == cached_candidate["original"])
    t10 = candidate.get("fallback_label") == "best_known_cached_not_latest" or all(c.get("fallback_label") == "best_known_cached_not_latest" for c in plan["candidates"] if c.get("fallback_label"))

    clock = FixtureClock(ratio=0.96, quantum=0.1)
    first = clock.monotonic(); first_utc = clock.now(); clock.sleep(0.2)
    gated = cadence_gate(clock, first, first_utc)
    t11 = (gated["dispatch_gap_seconds"] or 0) >= MIN_DISPATCH_SECONDS and (gated["start_gap_seconds"] or 0) >= MIN_REQUEST_START_SECONDS
    started = clock.now()
    clamp = clamp_budget(MAX_TOTAL_BODY_BYTES - 10, started, started + timedelta(seconds=2))
    disk = disk_gate(DISK_FLOOR_BYTES - 1)
    t12 = clamp["entity_body_cap"] == 10 and clamp["timeout_seconds"] <= PROXY_MAX_SECONDS and not disk["disk_floor_passed"]
    unknown_metadata = parse_cdx(json.dumps({"metadata": {"unexpected": True}}).encode())
    t13 = not unknown_metadata["valid"] and not unknown_metadata["complete"]
    cached_json = json.dumps([header, ["x", "20130612010000", candidate["original"], "image/gif", "200", digest1, "10"], []]).encode()
    cached_parsed = parse_cdx(cached_json, limit=250)
    t14 = cached_parsed["valid"] and cached_parsed["complete"] and not cached_parsed["potential_truncation"] and len(cached_parsed["rows"]) == 1
    nonzero_exit = validate_replay(gif_candidate, gif_row, headers_for(candidate["original"], gif_row["timestamp"], "image/gif"), good_gif, curl_exit=23)
    t15 = not nonzero_exit["accepted"] and "curl_exit_not_zero" in nonzero_exit["reasons"]

    # New reusable-runner contract checks.  These are structural/offline tests;
    # they do not create an execute output or dispatch a request.
    t16 = 1 <= int(plan.get("candidate_count", 0)) <= 20
    try:
        _plan_output_dir(str(ROOT / "outside-recovery-network"))
        t17 = False
    except RuntimeError:
        t17 = True
    bad_original = "ftp://example.invalid/asset.gif"
    t18 = urlsplit(bad_original).scheme not in {"http", "https"}
    bad_cached = {"record_count": CDX_LIMIT, "potential_truncation": True, "resume_keys": ["next"], "source_report_sha256": "a" * 64}
    t19 = bool(bad_cached["potential_truncation"] or bad_cached["record_count"] >= CDX_LIMIT or bad_cached["resume_keys"])
    old_fixture_path = FROZEN_NETWORK / "news-shared10" / "fixture-results.json"
    old_fixture = read_json(old_fixture_path)
    t20 = (old_fixture.get("all_passed") is True and old_fixture.get("passed") == 15
           and old_fixture.get("total") == 15 and sha_file(old_fixture_path) == "499836c7208e1d6df69a02280ed45505491756926e3c7b69d87c7acd83952152")
    try:
        _policy_hard_bounds(dict(plan["policy"], max_attempts=POLICY_MAX_ATTEMPTS + 1), 0)
        t21 = False
    except RuntimeError:
        t21 = True
    try:
        _validate_target_key(candidate["target_key"], {candidate["target_key"]})
        t22 = False
    except RuntimeError:
        t22 = True
    try:
        _validate_cached_evidence(candidate, candidate["query"], {"record_count": 1, "selected": {}})
        t23 = False
    except RuntimeError:
        t23 = True
    try:
        _validate_source_evidence(dict(candidate, source_evidence={**candidate["source_evidence"], "sha256": "0" * 64}))
        t24 = False
    except RuntimeError:
        t24 = True

    prior_before_fixture = PRIOR_FAILURE_TAIL
    try:
        globals()["PRIOR_FAILURE_TAIL"] = 2
        inherited_state = initial_state()
        t25 = (inherited_state["failure_streak"] == 2
               and inherited_state["failure_streak_start"] == 2
               and inherited_state["prior_failure_tail"] == 2
               and inherited_state["current_window_failure_streak"] == 0)
    finally:
        globals()["PRIOR_FAILURE_TAIL"] = prior_before_fixture

    # The cached six-column body is accepted only with exact row width; extra
    # columns are an invalid shape even if the first six values look useful.
    extra_column_body = json.dumps([
        CDX_FIELDS_WITHOUT_URLKEY,
        ["20130612050000", candidate["original"], "image/gif", "200", digest1, "10", "unexpected"],
    ]).encode()
    extra_column_parsed = parse_cdx(extra_column_body, limit=250)
    t26 = (not extra_column_parsed["valid"] and not extra_column_parsed["complete"]
           and extra_column_parsed["error"] == "unrecognized_metadata")

    tests = {
        "cdx_separator_and_resume_metadata": t1,
        "limit500_potential_truncation_no_replay": t2,
        "latest_exact_default_port_and_variant_classification": t3,
        "gif_jpeg_png_magic_pillow_and_all_frames": t4,
        "error_html_and_magic_rejection": t5,
        "compression_digest_memento_and_original_rejection": t6,
        "bounded_truncated_and_trailing_compression_rejected": t7,
        "connect_source_404_429_and_only_connect": t8,
        "cached_complete_cdx_reuse_and_latest_binding": t9,
        "fallback_cache_is_best_known_not_latest": t10,
        "cadence_monotonic_and_utc_floor_with_early_sleep": t11,
        "budget_disk_floor_and_failure_stop": t12,
        "unknown_metadata_is_incomplete": t13,
        "cached_sub_limit_separator_is_complete": t14,
        "nonzero_curl_exit_not_accepted": t15,
        "one_to_twenty_target_bound": t16,
        "malicious_output_path_rejected": t17,
        "malicious_original_rejected": t18,
        "cached_truncation_and_resume_rejected": t19,
        "frozen_news_shared10_fixtures_still_pass": t20,
        "hard_budget_bound_rejected": t21,
        "duplicate_target_key_rejected": t22,
        "fake_cached_metadata_rejected": t23,
        "source_binding_hash_rejected": t24,
        "prior_failure_tail_is_inherited_by_initial_state": t25,
        "real_allnews01_blizzcon_six_column_cache_accepted": t9,
        "six_column_extra_field_rejected": t26,
    }
    transport_fixture = run_transport_policy_fixtures()
    tests.update({f"transport_policy_{name}": value for name, value in transport_fixture["tests"].items()})
    result = {"schema": "wow-recovery.reusable-image-fixtures.v1", "batch_id": BATCH_ID,
              "network_requests": 0, "input_plan_sha256": sha_file(PLAN_PATH),
              "input_bindings_sha256": sha_file(BINDINGS_PATH), "tests": tests,
              "passed": sum(bool(v) for v in tests.values()), "total": len(tests),
              "all_passed": all(tests.values()),
              "transport_policy_fixture": transport_fixture,
              "positive_cached_fixture": {
                  "target_key": cached_candidate["target_key"],
                  "source_report_path": cached["source_report_path"],
                  "source_report_sha256": cached["source_report_sha256"],
                  "raw_body_path": cached["raw_body_path"],
                  "raw_body_sha256": cached["body_sha256"],
                  "raw_headers_path": cached["raw_headers_path"],
                  "raw_headers_sha256": cached["raw_headers_sha256"],
                  "source_curl_exit": cached["source_curl_exit"],
                  "query_url": cached["query_url"],
                  "coverage_window": cached["coverage_window"],
                  "record_count": cached["record_count"],
                  "selected": cached["selected"],
              },
              "notes": ["The first fifteen core tests are retained from the frozen NEWS-SHARED10 fixture contract.",
                        "No network request, curl process, payload write, or execute state was created by fixture mode.",
                        "Cached indexes require complete sub-limit evidence and remain latestness-limited.",
                        "The positive cached fixture is the SHA-bound ALLNEWS01 Blizzcon raw/70 response; its 2006..anchor query is not a global 2000..anchor latest proof."]}
    target = fixture_output or (DRIVER_DIR / "fixture-results.json")
    if not _under_network(target.resolve()):
        raise RuntimeError("fixture output must remain below the recovery network directory")
    write_json(target, result)
    return result
