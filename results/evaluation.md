Queries: 30 | Successful: 28 | Success rate: 93.33%
Acceptance cases: 27/27; limitation probes: 3.
| Mode | Input | Expected | Actual | Success | Latency (ms) |
|---|---|---|---|---|---|
| text | black shoes | 1 | 1 | Yes | 0.49 |
| text | blue shoes | 3 | 3 | Yes | 0.18 |
| text | Nike shoes under 100 dollars | 2 | 2 | Yes | 0.125 |
| text | Puma trainers | 3 | 3 | Yes | 0.168 |
| text | black bag | 15 | 15 | Yes | 0.161 |
| text | blue bag | 11 | 11 | Yes | 0.158 |
| text | white shirt | 7 | 7 | Yes | 0.167 |
| text | plaid shirt | 8 | 8 | Yes | 0.157 |
| text | dark sneakers | 1 | 1 | Yes | 0.163 |
| text | spaceship | None | None | Yes | 0.153 |
| text |  | None | None | Yes | 0.15 |
| text | find order O001 | O001 | O001 | Yes | 0.068 |
| text | where is my latest order | 20261001 | 20261001 | Yes | 0.015 |
| text | find order O002 | None | None | Yes | 0.011 |
| text | find order O002 | O002 | O002 | Yes | 0.009 |
| text | shoes | None | None | Yes | 0.099 |
| text | bag | 11 | 11 | Yes | 0.059 |
| text | shirt | 6 | 6 | Yes | 0.056 |
| image | data/images/p01.png | 1 | 1 | Yes | 24.292 |
| image | data/images/p03.png | 3 | 3 | Yes | 23.924 |
| image | data/images/p05.png | 5 | 5 | Yes | 24.936 |
| image | data/images/p11.png | 11 | 11 | Yes | 22.837 |
| image | data/images/query_blue_trainers.png | 3 | 3 | Yes | 3.91 |
| multimodal | blue shoes | 3 | 3 | Yes | 25.661 |
| multimodal | black bag | 15 | 15 | Yes | 26.624 |
| multimodal | shoes | 3 | 3 | Yes | 26.316 |
| audio | tests/fixtures/blue_shoes.wav | 3 | 3 | Yes | 1059.544 |
| audio | tests/fixtures/black_bag.wav | 15 | 1 | No | 719.963 |
| text | comfortable footwear | 3 | 3 | Yes | 0.167 |
| text | black shoes | 2 | 1 | No | 0.166 |
