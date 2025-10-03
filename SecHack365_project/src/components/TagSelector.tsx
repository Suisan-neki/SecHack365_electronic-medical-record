import React, { useState } from 'react';
import { Tag, SymptomCategory } from '../types';
import { useAppStore } from '../store/useAppStore';

interface TagSelectorProps {
  category: SymptomCategory;
  tags: Tag[];
  selectedTags: Tag[];
  onTagToggle: (tag: Tag) => void;
  isCollapsed?: boolean;
  onToggleCollapse?: () => void;
}

const TagSelector: React.FC<TagSelectorProps> = ({
  category,
  tags,
  selectedTags,
  onTagToggle,
  isCollapsed = false,
  onToggleCollapse
}) => {
  const categoryInfo = {
    cold: { name: '🤧 風邪・呼吸器系', color: '#e74c3c' },
    pain: { name: '💢 痛み系', color: '#e67e22' },
    gastro: { name: '🤢 消化器系', color: '#f39c12' },
    general: { name: '😴 全身症状', color: '#9b59b6' },
    cardio: { name: '❤️ 循環器系', color: '#e74c3c' },
    other: { name: '📝 その他', color: '#34495e' }
  };

  const info = categoryInfo[category];

  return (
    <div className="collapsible-category">
      <div 
        className="category-header" 
        onClick={onToggleCollapse}
        style={{ cursor: 'pointer' }}
      >
        <span className="category-toggle">
          {isCollapsed ? '▼' : '▲'}
        </span>
        <strong style={{ color: info.color }}>
          {info.name}
        </strong>
      </div>
      
      {!isCollapsed && (
        <div className="category-content">
          <div className="tag-buttons">
            {tags.map((tag) => {
              const isSelected = selectedTags.some(t => t.tag_id === tag.tag_id);
              return (
                <button
                  key={tag.tag_id}
                  className={`tag ${isSelected ? 'selected' : ''}`}
                  onClick={() => onTagToggle(tag)}
                >
                  {tag.tag_name}
                </button>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};

export default TagSelector;
