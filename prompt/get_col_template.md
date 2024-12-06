### Instruction
You are given a table with headers and sample rows. Each column represents a specific type of information. Your task is to write a brief description of what each column represents based on its header and sampled content. Make sure each description is concise and accurately reflects the meaning of the data in that column. Here is an example:

### Table Information
Header: | author | title | genre | publication year |
Sampled Rows:
| George Orwell       | "1984"                                  | dystopian  | 1949             |
| J.K. Rowling        | "Harry Potter and the Sorcerer's Stone" | fantasy    | 1997             |
| J.R.R. Tolkien      | "The Hobbit"                            | fantasy    | 1937             |
| F. Scott Fitzgerald | "The Great Gatsby"                      | fiction    | 1925             |
| Harper Lee          | "To Kill a Mockingbird"                 | fiction    | 1960             |

### Output

Col1 ## author: The name of the person who wrote the book.
Col2 ## title: The name of the book, often shown with quotation marks.
Col3 ## genre: The category or type of literature the book belongs to.
Col4 ## publication year: The year the book was originally published.

### Attention

1. Ensure descriptions are brief and logically clear.
2. Do not generate any additional explanations or content beyond what is requested.

### Table Information
Header:{header}
Sampled Rows:
{sampled_rows}

### Output