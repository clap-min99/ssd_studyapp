import { useState, useEffect } from 'react';
import { api } from '../api/client';

function Categories() {
  const [tags, setTags] = useState([]);
  const [selected, setSelected] = useState(null);
  const [articles, setArticles] = useState([]);

  useEffect(() => {
    api.getTags().then(setTags);
  }, []);

  const selectTag = async (tag) => {
    setSelected(tag);
    const data = await api.getTagArticles(tag.slug);
    setArticles(data);
  };

  return (
    <div>
      <h1>카테고리</h1>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginBottom: '16px' }}>
        {tags.map(t => (
          <button
            key={t.slug}
            className={`pill ${t.category === 'ssd' ? 'badge-ssd' : 'badge-automotive'}`}
            onClick={() => selectTag(t)}
          >
            {t.name}
          </button>
        ))}
      </div>

      {selected && (
        <>
          <p className="status-message">{selected.description}</p>
          {articles.map(a => (
            <div key={a.id} className="card">
              <h3>{a.title}</h3>
              <p>{a.summary}</p>
            </div>
          ))}
        </>
      )}
    </div>
  );
}

export default Categories;