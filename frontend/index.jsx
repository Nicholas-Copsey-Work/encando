const { useState } = React;
const api = new API();

const App = () => {
    const [input, setInput] = useState('');
    const [response, setResponse] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const result = await api.compliance.post({ html: input });
            setResponse(result);
        } catch (error) {
            console.error('Error:', error);
        }
    };

    return (
        <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
            <h1>Accessibility Checker</h1>
            <form onSubmit={handleSubmit}>
                <textarea
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Enter your text here..."
                    rows="10"
                    cols="50"
                    style={{ width: '100%', marginBottom: '10px' }}
                />
                <br />
                <button type="submit" style={{ padding: '10px 20px', cursor: 'pointer' }}>
                    Submit
                </button>
            </form>
            {response && (
                <div style={{ marginTop: '20px' }}>
                    <h2>Response:</h2>
                    <p><strong>Passes:</strong> {response.passes ? 'Yes' : 'No'}</p>
                    {response.issues && response.issues.length > 0 && (
                        <div>
                            <h3>Issues:</h3>
                            <ul>
                                {response.issues.map((issue, index) => (
                                    <li key={index} style={{ marginBottom: '10px' }}>
                                        <p><strong>Rule ID:</strong> {issue.ruleId}</p>
                                        <p><strong>Message:</strong> {issue.message}</p>
                                        <p><strong>Element:</strong> {issue.element}</p>
                                        <p><strong>Selector:</strong> {issue.selector}</p>
                                        <pre style={{ background: '#f4f4f4', padding: '10px' }}>
                                            <code>{issue.codeSnippet}</code>
                                        </pre>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

const rootElement = document.getElementById('root');
ReactDOM.render(<App />, rootElement);