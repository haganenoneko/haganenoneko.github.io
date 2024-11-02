// File: .vscode/linkReferences.js
const fs = require('fs');

const filePath = process.env.VSCODE_FILE;

if (!filePath) {
    console.error('No file open');
    process.exit(1);
}

const processReferences = (filePath) => {
    try {
        let content = fs.readFileSync(filePath, 'utf8');
        
        // First, add reference tags if they don't exist
        const refSection = content.split('## References')[1];
        if (refSection) {
            const references = refSection.trim().split('\n');
            const processedRefs = references.map(ref => {
                // Skip empty lines and lines that already have tags
                if (!ref.trim() || ref.includes('<a id="ref-')) {
                    return ref;
                }
                
                // Match reference numbers at the start of lines
                const match = ref.match(/^(\d+)\./);
                if (match) {
                    const refNum = match[1];
                    return `${refNum}. <a id="ref-${refNum}"></a>${ref.slice(match[0].length)}`;
                }
                return ref;
            });
            
            content = content.split('## References')[0] + '## References\n' + processedRefs.join('\n');
        }

        // Then, process the reference links in the main text
        // Matches patterns like [1], [1, 3], [2-4], or [1, 3-5, 7]
        const regex = /\[(\d+(?:-\d+)?(?:,\s*\d+(?:-\d+)?)*)\](?!\])/g;

        content = content.replace(regex, (match, refs) => {
            const refLinks = refs.split(',').flatMap(ref => {
                ref = ref.trim();
                if (ref.includes('-')) {
                    const [start, end] = ref.split('-').map(Number);
                    return Array.from(
                        { length: end - start + 1 }, 
                        (_, i) => start + i
                    );
                } else {
                    return [parseInt(ref, 10)];
                }
            }).map(ref => `[\[${ref}\]](#ref-${ref})`);

            return refLinks.join(', ');
        });

        fs.writeFileSync(filePath, content, 'utf8');
        console.log('Updated references and added reference tags');
    } catch (error) {
        console.error(`Error processing file: ${error.message}`);
        process.exit(1);
    }
};

processReferences(filePath);