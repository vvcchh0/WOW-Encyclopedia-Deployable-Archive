# gallery-late-rest10a adapter diff

- Frozen template: `research/continuous-recovery-20261019/network/gallery-late-gap01/gallery_late_gap01_driver_v1.py` SHA256 `99e3abf059bfbb0398a0a6d225939620a836bcd5278e9fdbd1a9448043b4aae8`.
- New packet driver: `research/continuous-recovery-20261019/network/gallery-late-rest10a/gallery_late_rest10a_driver_v1.py` SHA256 `ccd1b2b9810d274545e20f99940c1cb1a32c79c07bdb95a83408ef0c07df6541`.
- Full unified diff: `research/continuous-recovery-20261019/network/gallery-late-rest10a/driver-diff.patch` SHA256 `e124e6b233a6cf1bc745045778d97de8e89c9454539f537a6cb5738d7b3410f9`.

Changed contract surface:

- Target set expands from the old paired two-prefix contract to exactly the ten frozen late-rest candidates.
- Batch window becomes 900 seconds; max attempts and explicit max requests become 24; total CDX body budget becomes 32 MiB; per-response budget remains 8 MiB.
- The new validation gate binds the zero-request late coverage ledger, ten-prefix manifest, latest accepted global news20f tail0, accepted control tail0, and accepted gallery gap01 tail0.
- `validate_inputs`, `fixture`, `plan_for_run`, and the execute loop cap are packet-local changes. The transport/parser/identity/projecting functions remain byte-level source copies except for constants they read.
- CDX remains index-only: no payload replay, no redirect follow, no filename expansion, no automatic resume continuation. Resume keys or limit saturation remain incomplete.

AST function comparison:

- `_remaining_clamp`: unchanged (old c9fb4c9a6861ce7717e042c3818e459538491ab8d6d83d2bef14d7194ddbcd81, new c9fb4c9a6861ce7717e042c3818e459538491ab8d6d83d2bef14d7194ddbcd81)
- `_restart_last_dispatch`: unchanged (old ffd57f61f5d17a8284c1057c36913c0942708058d8d506e1eba69ec2eb18975f, new ffd57f61f5d17a8284c1057c36913c0942708058d8d506e1eba69ec2eb18975f)
- `_schedule_next`: unchanged (old 56362ca57d8adb15c136bf334889fe181651a8bb5f1631391835777495e9242b, new 56362ca57d8adb15c136bf334889fe181651a8bb5f1631391835777495e9242b)
- `canonical_query_url`: unchanged (old 2e06174a71da797f661348c37485975b530c8b0b4c127bfded0db69e4d690ff1, new 2e06174a71da797f661348c37485975b530c8b0b4c127bfded0db69e4d690ff1)
- `cf`: unchanged (old d48f4274d3c31e923a2c6df419c28f7b1518902c25db9ac593cc3afcae904e7f, new d48f4274d3c31e923a2c6df419c28f7b1518902c25db9ac593cc3afcae904e7f)
- `execute`: changed (old fd8bef9ffa03f08e24063ce70d34c923f3f9d001856a1a5e2c0f5a072ba57401, new 2fdccdfebb0f326bc88549d6c0ec0d00a8c4ff2642b27de7d36d312a0d7c5276)
- `fixture`: changed (old cd4ad8ebec89520ee760ab30af79cccdae9dd8ee3f4f98751b8635f0ecd20a86, new f35697a62837b980a2c85794fa4b64dfabfaaf6a250fd8a7a674b373bdbbf63a)
- `free_bytes`: unchanged (old 7f14c9c4bc77744187f044d753a19a78697045d8de00025b5541d7850ba4bca1, new 7f14c9c4bc77744187f044d753a19a78697045d8de00025b5541d7850ba4bca1)
- `headers`: unchanged (old dbc0f0faf3b943027dd64406835ab92ce49314663bf998c33f06e7fa28a4a7a2, new dbc0f0faf3b943027dd64406835ab92ce49314663bf998c33f06e7fa28a4a7a2)
- `iso`: unchanged (old 8ff62a935f8cdbfbd2e7f83f57f231f51e7a80a1431bc7ae058b89e10dcc5b94, new 8ff62a935f8cdbfbd2e7f83f57f231f51e7a80a1431bc7ae058b89e10dcc5b94)
- `main`: unchanged (old 557f0730a58568267c7b4f5d8f04126a126a234bc01084d488a7065e288e9b2e, new 557f0730a58568267c7b4f5d8f04126a126a234bc01084d488a7065e288e9b2e)
- `now`: unchanged (old 53caf2f8abcec7705657f652f053be4ea16a21102c6286fcc99ea4cf8585bd7e, new 53caf2f8abcec7705657f652f053be4ea16a21102c6286fcc99ea4cf8585bd7e)
- `parse_cdx`: unchanged (old c3bf87b58186945135a80e13aa50bdea43ec2dd8ab4cc5704a61df24357c5cce, new c3bf87b58186945135a80e13aa50bdea43ec2dd8ab4cc5704a61df24357c5cce)
- `parse_iso`: unchanged (old 01af09bde28d6d7e81bff9324e155cd763e7f54cd91ad11a8fc418f0faa20985, new 01af09bde28d6d7e81bff9324e155cd763e7f54cd91ad11a8fc418f0faa20985)
- `phase`: unchanged (old e32d16389d7b433b97df7c4dc489eda1510b4cc4a189387a41bf951a2a8cdde1, new e32d16389d7b433b97df7c4dc489eda1510b4cc4a189387a41bf951a2a8cdde1)
- `plan_for_run`: changed (old f1bbbfa0f586ac2fb4968112e62b7094cf37dc83d2cbe6e0f16dcda512fc406b, new 698f0302dee420a4f8a7d4400f75e26053027bc68ed1c367f6a03906bce994c4)
- `project_rows`: unchanged (old 37894d9a51e3116142e6ec161073022a520d39113cc00b60658a794301081618, new 37894d9a51e3116142e6ec161073022a520d39113cc00b60658a794301081618)
- `public_attempt`: unchanged (old 4698ba1facb2bfa44d070821f999a2d4ad4a4b2360714e48cf999f0ad3c1aa75, new 4698ba1facb2bfa44d070821f999a2d4ad4a4b2360714e48cf999f0ad3c1aa75)
- `read_json`: unchanged (old 1924d1366955ffd4d13986b4ec21eb1ec2b4bf0a0a3dff1d77574d995fe2ba49, new 1924d1366955ffd4d13986b4ec21eb1ec2b4bf0a0a3dff1d77574d995fe2ba49)
- `rel`: unchanged (old 02f3e9c2d4435bacb81cdd842dc6ab509a6f9047857a7568b77d4e433796c5b9, new 02f3e9c2d4435bacb81cdd842dc6ab509a6f9047857a7568b77d4e433796c5b9)
- `request`: unchanged (old 2188d3cee48ebfbdfb4b6a97b8849ae11f1761edd98637e278be376d4b975cc0, new 2188d3cee48ebfbdfb4b6a97b8849ae11f1761edd98637e278be376d4b975cc0)
- `same_origin`: unchanged (old 4bb588a3f5cdf5415447a11590d2c86199a61807d5b414b7b30f7e8a3d36d66b, new 4bb588a3f5cdf5415447a11590d2c86199a61807d5b414b7b30f7e8a3d36d66b)
- `sha`: unchanged (old ab85ca9d027eadb8edccc4e985752f52b94ca9d25bd31c9578882e81c388eaf6, new ab85ca9d027eadb8edccc4e985752f52b94ca9d25bd31c9578882e81c388eaf6)
- `status`: unchanged (old f0ab0e2f8adf40793f0fd6ddfcfc8cbca4442a77a94ebdd88786854cc9551bf8, new f0ab0e2f8adf40793f0fd6ddfcfc8cbca4442a77a94ebdd88786854cc9551bf8)
- `validate_inputs`: changed (old be38b00d852bc9da1377c3c5ab4cb16294102d3bee7111aaa6c6974ad50140f2, new 10dff2af3b87848f96114dbc84c59e4fea218d42acd3a1688f3a7eb1e0b63876)
- `write_json`: unchanged (old 2373ef2617fa737142c900c35a2e74abed8786e03c431b298592dbf8b956071d, new 2373ef2617fa737142c900c35a2e74abed8786e03c431b298592dbf8b956071d)
