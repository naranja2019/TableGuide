### Instruction

You are given a question and the headers of a table. Based on the question content and the table headers, link the headers from the table schema to relevant parts of the question by placing each linked header in square brackets [ ].

### Given Information

1. Question: how many consecutive songs were by the album leaf?
2. Table Header: ["artist", "song", "soundtrack", "episode(s)", "notes"]

### Generation

how many consecutive songs[song] were by the album leaf[artist]? 

### Attention

1. Output only the modified question, without any additional content.
2. Place each table header used for linking in square brackets [ ].

---

### Given Information

1. Question: {question}
2. Table Header: {headers}

### Your Generation