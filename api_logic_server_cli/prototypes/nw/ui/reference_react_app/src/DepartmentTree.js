import React, { useState, useEffect } from 'react';

const DepartmentTree = () => {
  const [departments, setDepartments] = useState([]);
  const [expandedNodes, setExpandedNodes] = useState(new Set());

  useEffect(() => {
    // Fetch departments from API Logic Server
    fetchDepartments();
  }, []);

  const fetchDepartments = async () => {
    try {
      const response = await fetch('/api/Department');
      const data = await response.json();
      setDepartments(buildTree(data.data));
    } catch (error) {
      console.error('Error fetching departments:', error);
    }
  };

  const buildTree = (flatData) => {
    const map = {};
    const tree = [];

    // Create a map of all departments
    flatData.forEach(dept => {
      map[dept.Id] = { ...dept, children: [] };
    });

    // Build the tree structure
    flatData.forEach(dept => {
      if (dept.DepartmentId && map[dept.DepartmentId]) {
        // This department has a parent
        map[dept.DepartmentId].children.push(map[dept.Id]);
      } else {
        // This is a root department
        tree.push(map[dept.Id]);
      }
    });

    return tree;
  };

  const toggleNode = (nodeId) => {
    const newExpanded = new Set(expandedNodes);
    if (newExpanded.has(nodeId)) {
      newExpanded.delete(nodeId);
    } else {
      newExpanded.add(nodeId);
    }
    setExpandedNodes(newExpanded);
  };

  const TreeNode = ({ node, level = 0 }) => {
    const hasChildren = node.children && node.children.length > 0;
    const isExpanded = expandedNodes.has(node.Id);

    return (
      <div className="tree-node">
        <div 
          className="tree-node-content"
          style={{ paddingLeft: `${level * 20}px` }}
        >
          {hasChildren && (
            <span 
              className={`tree-toggle ${isExpanded ? 'expanded' : 'collapsed'}`}
              onClick={() => toggleNode(node.Id)}
            >
              {isExpanded ? '▼' : '▶'}
            </span>
          )}
          <span className="tree-node-label">
            {node.DepartmentName} (Level: {node.SecurityLevel})
          </span>
        </div>
        
        {hasChildren && isExpanded && (
          <div className="tree-children">
            {node.children.map(child => (
              <TreeNode 
                key={child.Id} 
                node={child} 
                level={level + 1} 
              />
            ))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="department-tree">
      <h2>Department Hierarchy</h2>
      <div className="tree-container">
        {departments.map(dept => (
          <TreeNode key={dept.Id} node={dept} />
        ))}
      </div>
      
      <style jsx>{`
        .department-tree {
          padding: 20px;
          font-family: Arial, sans-serif;
        }
        
        .tree-container {
          border: 1px solid #ddd;
          border-radius: 4px;
          padding: 10px;
          background-color: #f9f9f9;
        }
        
        .tree-node-content {
          display: flex;
          align-items: center;
          padding: 4px 0;
          cursor: pointer;
        }
        
        .tree-node-content:hover {
          background-color: #e6f3ff;
        }
        
        .tree-toggle {
          margin-right: 8px;
          font-size: 12px;
          color: #666;
          cursor: pointer;
          user-select: none;
        }
        
        .tree-node-label {
          font-weight: 500;
        }
        
        .tree-children {
          border-left: 1px dashed #ccc;
          margin-left: 10px;
        }
      `}</style>
    </div>
  );
};

export default DepartmentTree;
