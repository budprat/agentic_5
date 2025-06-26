# NotionAI MCP Server Usage Rules

## Primary Rule: Write-Only to "AI" Page
**All content creation, updates, and modifications must ONLY be written to the "AI" page (ID: 21e0f849-e0a2-80c3-8b72-ccb0a1b61ab9)**

## Page Access Rules

### 1. Writing Operations
- **ONLY write to**: "AI" page (🖲️)
- **Never write to**: Any other pages or databases
- **Page ID for writing**: `21e0f849-e0a2-80c3-8b72-ccb0a1b61ab9`

### 2. Reading Operations
- **Can read from**: All accessible pages (90+ pages)
- **Use for reference**: All other pages should be treated as read-only sources
- **Purpose**: Gather information, context, and data for analysis

## Implementation Guidelines

### When User Asks to Save/Write Content:
1. Always use the "AI" page as the destination
2. Use `mcp__notionAI__API-patch-block-children` to append content
3. Structure content appropriately within the AI page
4. Create clear sections/headings for different topics

### When User Asks to Read/Retrieve Content:
1. Search across all pages using `mcp__notionAI__API-post-search`
2. Read specific pages using appropriate API calls
3. Never modify these pages - only extract information

### Content Organization in AI Page:
- Use clear headings for different topics
- Add timestamps for entries
- Maintain logical structure
- Use markdown formatting for clarity

## API Usage Patterns

### For Writing (AI Page Only):
```
Tool: mcp__notionAI__API-patch-block-children
Parameters:
- block_id: "21e0f849-e0a2-80c3-8b72-ccb0a1b61ab9"
- children: [content blocks]
```

### For Reading (All Pages):
```
Tool: mcp__notionAI__API-post-search
Tool: mcp__notionAI__API-retrieve-a-page
Tool: mcp__notionAI__API-get-block-children
```

## Error Prevention
- Always verify page ID before writing
- Double-check that writing operations target only the AI page
- If user requests writing to another page, redirect to AI page
- Maintain audit trail of all write operations

## Usage Examples

### Correct Usage:
✅ "Save this analysis" → Write to AI page
✅ "Document this code" → Write to AI page
✅ "Create a summary" → Write to AI page
✅ "Read from Veo3 prompts" → Read from respective page

### Incorrect Usage:
❌ Writing to any page other than AI
❌ Modifying existing content in other pages
❌ Creating new pages or databases

## Compliance Check
Before any write operation:
1. Is the target page "AI"? 
2. Is the page ID correct (21e0f849-e0a2-80c3-8b72-ccb0a1b61ab9)?
3. Is the content appropriate for the AI page?

If any answer is NO, stop and redirect to proper usage.

---
Last Updated: June 26, 2025
These rules ensure proper usage of NotionAI MCP server while maintaining data integrity across the workspace.