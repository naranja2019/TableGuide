### Instruction
You are given a table with a header row and content rows. Each cell in the table contains specific information corresponding to the columns in the header. Your task is to create a template that generates a natural language description for each row in the table. Use the words from the header as placeholders in the template, and ensure the placeholders are written exactly as they appear in the header row. Here’s an example for clarity:

### Table Information
Header: | author | title | genre | publication year |
Sampled Rows:
| George Orwell       | "1984"                                  | dystopian  | 1949             |
| J.K. Rowling        | "Harry Potter and the Sorcerer's Stone" | fantasy    | 1997             |
| J.R.R. Tolkien      | "The Hobbit"                            | fantasy    | 1937             |
| F. Scott Fitzgerald | "The Great Gatsby"                      | fiction    | 1925             |
| Harper Lee          | "To Kill a Mockingbird"                 | fiction    | 1960             |

### Template Example

The book titled {{title}} by author {{author}} belongs to the {{genre}} genre and was published in {{publication year}}.

### Attention

1. Use the exact terms from the header as placeholders.
2. Ensure each header term appears in the template.
3. Design the template so that each row’s values can generate a complete sentence when placed into the placeholders.
4. The answer only contains the template, without any other explanations or introductory language.

### Table Information
Header:{header}
Sampled Rows:
{sampled_rows}

### Template