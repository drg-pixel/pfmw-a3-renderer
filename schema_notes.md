# PFMW A.3 Required Matrix Contract

Required `matrix` keys:

- `TODAY / RUN`
- `NEXT / WHEN STABLE`
- `FUTURE / BUILD CAPACITY`

Required block keys inside every phase:

- `B1`
- `B2`
- `B3`
- `B4`
- `B5`
- `B6`
- `B7`

Required cell keys inside every block:

- `do`
- `dose`
- `test`
- `rule`

The renderer fails if any row, block, or cell key is missing.
