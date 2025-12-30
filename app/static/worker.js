/**
 * Directory Indexer Web Worker - Optimized Hybrid
 * Fast processing with periodic UI yields
 */

// ==================== OPTIMIZED PROCESSING ====================

/**
 * Sort files: directories first, then alphabetically
 */
function sortFiles(files) {
    return files.sort((a, b) => {
        if (a.isDir !== b.isDir) return a.isDir ? -1 : 1;
        return a.path.localeCompare(b.path, undefined, { sensitivity: 'base' });
    });
}

/**
 * Build hierarchy with numbering - optimized single pass
 */
function buildHierarchy(files, onProgress) {
    const tree = [];
    const pathToNode = new Map();
    let processed = 0;
    const yieldInterval = 100;
    
    for (const file of files) {
        const parts = file.path.split('/').filter(p => p);
        let currentLevel = tree;
        let currentPath = '';
        let numbering = [];
        
        for (let i = 0; i < parts.length; i++) {
            const part = parts[i];
            currentPath = currentPath ? `${currentPath}/${part}` : part;
            const isLast = i === parts.length - 1;
            
            let existing = pathToNode.get(currentPath);
            
            if (!existing) {
                const position = currentLevel.length + 1;
                const newNumbering = [...numbering, position];
                
                existing = {
                    number: newNumbering.join('.'),
                    name: part,
                    type: isLast && !file.isDir ? 'file' : 'directory',
                    path: currentPath,
                    children: []
                };
                
                currentLevel.push(existing);
                pathToNode.set(currentPath, existing);
            }
            
            numbering = existing.number.split('.').map(Number);
            currentLevel = existing.children;
        }
        
        processed++;
        if (onProgress && processed % yieldInterval === 0) {
            onProgress(processed, files.length);
        }
    }
    
    return tree;
}

/**
 * Count items in hierarchy
 */
function countItems(items) {
    let count = items.length;
    for (const item of items) {
        if (item.children) count += countItems(item.children);
    }
    return count;
}

// ==================== OUTPUT GENERATORS ====================

function escapeXml(str) {
    return str.replace(/[<>&'"]/g, c => 
        ({ '<': '&lt;', '>': '&gt;', '&': '&amp;', "'": '&apos;', '"': '&quot;' })[c]
    );
}

function generateJSON(data) {
    return JSON.stringify(data, null, 2);
}

function generateXML(data, onProgress) {
    let xml = '<?xml version="1.0" encoding="UTF-8"?>\n';
    xml += `<directory_index root_path="${escapeXml(data.root)}">\n`;
    
    let count = 0;
    const yieldInterval = 500;
    
    function addItems(items, indent = 1) {
        const spaces = '  '.repeat(indent);
        for (const item of items) {
            xml += `${spaces}<item number="${item.number}" type="${item.type}">\n`;
            xml += `${spaces}  <name>${escapeXml(item.name)}</name>\n`;
            xml += `${spaces}  <path>${escapeXml(item.path)}</path>\n`;
            
            if (item.children?.length > 0) {
                xml += `${spaces}  <children>\n`;
                addItems(item.children, indent + 2);
                xml += `${spaces}  </children>\n`;
            }
            
            xml += `${spaces}</item>\n`;
            count++;
            
            if (onProgress && count % yieldInterval === 0) {
                onProgress(count);
            }
        }
    }
    
    addItems(data.hierarchy);
    xml += '</directory_index>';
    return xml;
}

function generateTXT(data, onProgress) {
    let txt = `Directory Index: ${data.root}\n`;
    txt += '='.repeat(80) + '\n\n';
    
    let count = 0;
    const yieldInterval = 500;
    
    function formatItem(item, depth = 0) {
        const indent = '  '.repeat(depth);
        const icon = item.type === 'directory' ? '📁' : '📄';
        txt += `${indent}${item.number}. ${icon} ${item.name}\n`;
        count++;
        
        if (onProgress && count % yieldInterval === 0) {
            onProgress(count);
        }
        
        item.children?.forEach(child => formatItem(child, depth + 1));
    }
    
    data.hierarchy.forEach(item => formatItem(item));
    return txt;
}

// ==================== MESSAGE HANDLERS ====================

self.onmessage = function(e) {
    const { action, payload } = e.data;
    
    switch (action) {
        case 'processFiles':
            processFiles(payload);
            break;
            
        case 'generateOutputs':
            generateOutputs(payload);
            break;
            
        default:
            self.postMessage({ type: 'error', message: `Unknown action: ${action}` });
    }
};

function processFiles({ files }) {
    try {
        self.postMessage({ type: 'progress', step: 'sort', message: 'Sorting files...' });
        
        const sorted = sortFiles(files);
        
        self.postMessage({ type: 'progress', step: 'hierarchy', message: 'Building hierarchy...' });
        
        const hierarchy = buildHierarchy(sorted, (processed, total) => {
            self.postMessage({
                type: 'progress',
                step: 'hierarchy',
                processed,
                total,
                message: `Building hierarchy... ${processed}/${total}`
            });
        });
        
        self.postMessage({
            type: 'hierarchyComplete',
            hierarchy,
            itemCount: countItems(hierarchy)
        });
        
    } catch (error) {
        self.postMessage({ type: 'error', message: error.message });
    }
}

function generateOutputs({ hierarchy, folderName, formats }) {
    try {
        const data = { root: folderName, hierarchy };
        const outputs = {};
        
        if (formats.json) {
            self.postMessage({ type: 'progress', step: 'json', message: 'Generating JSON...' });
            outputs.json = generateJSON(data);
        }
        
        if (formats.xml) {
            self.postMessage({ type: 'progress', step: 'xml', message: 'Generating XML...' });
            outputs.xml = generateXML(data, count => {
                self.postMessage({ type: 'progress', step: 'xml', count });
            });
        }
        
        if (formats.txt) {
            self.postMessage({ type: 'progress', step: 'txt', message: 'Generating TXT...' });
            outputs.txt = generateTXT(data, count => {
                self.postMessage({ type: 'progress', step: 'txt', count });
            });
        }
        
        self.postMessage({ type: 'outputsComplete', outputs });
        
    } catch (error) {
        self.postMessage({ type: 'error', message: error.message });
    }
}
