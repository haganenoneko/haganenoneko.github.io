const fs = require("fs");
const path = require("path");
const readline = require("readline");

const POSTS_DIR = path.join(process.cwd(), "_posts");

// Function to get today's date in YYYY-MM-DD format
const getDate = () => {
  return new Date().toISOString().split("T")[0];
};

// Format tags for YAML frontmatter
// const formatTags = (tagsInput) => {
//     if (!tagsInput) return '';
//     const tagsArray = tagsInput.split(',').map(tag => tag.trim());
//     return `tags:\n  - ${tagsArray.join('\n  - ')}`;
// };
const formatList = (listInput, name) => {
  if (!listInput) return "";
  const itemsArray = listInput.split(",").map((item) => item.trim());
  return `${name}:\n  - ${itemsArray.join("\n  - ")}`;
};

// Function to prompt user for input
const promptUser = (question) => {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });
  return new Promise((resolve) =>
    rl.question(question, (answer) => {
      rl.close();
      resolve(answer);
    })
  );
};

const createMarkdownFile = async () => {
  // Prompt for title
  const title = await promptUser(
    "Enter the blog post title (use hyphens for spaces): "
  );
  if (!title) {
    console.error("No title provided");
    process.exit(1);
  }

  // Prompt for tags
  const categories = await promptUser(
    "Enter comma-separated categories (leave blank for none): "
  );

  // Prompt for tags
  const tags = await promptUser(
    "Enter comma-separated tags (leave blank for none): "
  );

  // Create file details
  const date = getDate();
  const fileName = `${date}_${title}.md`;
  const filePath = path.join(POSTS_DIR, fileName);

  // Ensure the _posts directory exists
  if (!fs.existsSync(POSTS_DIR)) {
    fs.mkdirSync(POSTS_DIR, { recursive: true });
  }

  // Format permalink and tags
  const permalink = `/posts/${encodeURIComponent(
    fileName.replace(/ /g, "-").replace(".md", "")
  )}`;
  const tagsFormatted = formatList(tags, "tags");
  const categoriesFormatted = formatList(categories, "categories");

  // Markdown file content with frontmatter
  const content =
    `---\n` +
    `title: ${title.replace(/-/g, " ")}\n` +
    `date: ${date}\n` +
    `permalink: ${permalink}\n` +
    (categoriesFormatted ? `${categoriesFormatted}\n` : "") +
    (tagsFormatted ? `${tagsFormatted}\n` : "") +
    `---\n\n` +
    `# ${title.replace(/-/g, " ")}\n`;

  // Write to file
  fs.writeFileSync(filePath, content);
  console.log(`Created ${fileName} with permalink: ${permalink}`);
};

createMarkdownFile().catch(console.error);
