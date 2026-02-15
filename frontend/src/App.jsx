import { useState, useEffect, createContext, useContext } from 'react'
import { BrowserRouter, Routes, Route, Navigate, Link, useNavigate } from 'react-router-dom'
import axios from 'axios'

// Configure axios
axios.defaults.baseURL = '/api'

// Auth Context
const AuthContext = createContext(null)

export const useAuth = () => useContext(AuthContext)

const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null)
    const [token, setToken] = useState(localStorage.getItem('token'))
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        if (token) {
            axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
            fetchUser()
        } else {
            setLoading(false)
        }
    }, [token])

    const fetchUser = async () => {
        try {
            const res = await axios.get('/auth/profile/')
            setUser(res.data)
        } catch (err) {
            logout()
        } finally {
            setLoading(false)
        }
    }

    const login = async (email, password) => {
        const res = await axios.post('/auth/login/', { email, password })
        const { token, user } = res.data
        localStorage.setItem('token', token)
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
        setToken(token)
        setUser(user)
        return user
    }

    const register = async (data) => {
        const res = await axios.post('/auth/register/', data)
        return res.data
    }

    const logout = () => {
        localStorage.removeItem('token')
        delete axios.defaults.headers.common['Authorization']
        setToken(null)
        setUser(null)
    }

    return (
        <AuthContext.Provider value={{ user, token, login, register, logout, loading }}>
            {children}
        </AuthContext.Provider>
    )
}

// Protected Route
const ProtectedRoute = ({ children }) => {
    const { user, loading } = useAuth()

    if (loading) {
        return (
            <div className="auth-container">
                <div className="spinner"></div>
            </div>
        )
    }

    return user ? children : <Navigate to="/login" />
}

// Navbar Component
const Navbar = () => {
    const { user, logout } = useAuth()

    return (
        <nav className="navbar">
            <div className="container navbar-content">
                <Link to="/" className="logo">
                    <span className="logo-icon">🔐</span>
                    PDF Encrypt
                </Link>

                <div className="nav-links">
                    <Link to="/" className="nav-link">Home</Link>
                    <Link to="/decrypt" className="nav-link">Decrypt</Link>
                    {user ? (
                        <>
                            <Link to="/dashboard" className="nav-link">Dashboard</Link>
                            <button onClick={logout} className="btn btn-secondary">
                                Logout
                            </button>
                        </>
                    ) : (
                        <>
                            <Link to="/login" className="nav-link">Login</Link>
                            <Link to="/register" className="btn btn-primary">
                                Get Started
                            </Link>
                        </>
                    )}
                </div>
            </div>
        </nav>
    )
}

// Home Page
const HomePage = () => {
    return (
        <div className="fade-in">
            <section className="hero container">
                <h1>Secure PDF Encryption</h1>
                <p>
                    Protect your sensitive documents with military-grade DCKP-ES encryption.
                    Share confidently with pixel-level security.
                </p>
                <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
                    <Link to="/register" className="btn btn-primary btn-lg">
                        Start Encrypting
                    </Link>
                    <Link to="/decrypt" className="btn btn-secondary btn-lg">
                        Decrypt File
                    </Link>
                </div>
            </section>

            <section className="container">
                <div className="features-grid">
                    <div className="card feature-card">
                        <div className="feature-icon">📄</div>
                        <h3 className="feature-title">PDF to Images</h3>
                        <p>Each page is converted to high-quality images for pixel-level processing</p>
                    </div>

                    <div className="card feature-card">
                        <div className="feature-icon">🧩</div>
                        <h3 className="feature-title">32-Pixel Chunks</h3>
                        <p>Images are divided into secure chunks for enhanced encryption</p>
                    </div>

                    <div className="card feature-card">
                        <div className="feature-icon">🔀</div>
                        <h3 className="feature-title">Chaos Shuffling</h3>
                        <p>Pixel positions are randomized using chaos theory algorithms</p>
                    </div>

                    <div className="card feature-card">
                        <div className="feature-icon">🔐</div>
                        <h3 className="feature-title">DCKP-ES Encryption</h3>
                        <p>Dynamic Chaos Key Pixel Encryption for unbreakable security</p>
                    </div>

                    <div className="card feature-card">
                        <div className="feature-icon">📧</div>
                        <h3 className="feature-title">Email Delivery</h3>
                        <p>Encrypted files delivered directly to receiver's inbox</p>
                    </div>

                    <div className="card feature-card">
                        <div className="feature-icon">🔓</div>
                        <h3 className="feature-title">Easy Decryption</h3>
                        <p>Recipients decrypt with a simple key - no account needed</p>
                    </div>
                </div>
            </section>
        </div>
    )
}

// Login Page
const LoginPage = () => {
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [error, setError] = useState('')
    const [loading, setLoading] = useState(false)
    const { login } = useAuth()
    const navigate = useNavigate()

    const handleSubmit = async (e) => {
        e.preventDefault()
        setError('')
        setLoading(true)

        try {
            await login(email, password)
            navigate('/dashboard')
        } catch (err) {
            setError(err.response?.data?.non_field_errors?.[0] || 'Login failed')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="auth-container fade-in">
            <div className="card auth-card">
                <div className="auth-header">
                    <div className="auth-icon">🔐</div>
                    <h2>Welcome Back</h2>
                    <p>Sign in to encrypt your PDFs</p>
                </div>

                {error && <div className="alert alert-error">⚠️ {error}</div>}

                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label className="form-label">Email</label>
                        <input
                            type="email"
                            className="form-input"
                            placeholder="you@example.com"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label className="form-label">Password</label>
                        <input
                            type="password"
                            className="form-input"
                            placeholder="••••••••"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                        />
                    </div>

                    <button type="submit" className="btn btn-primary btn-lg" style={{ width: '100%' }} disabled={loading}>
                        {loading ? 'Signing in...' : 'Sign In'}
                    </button>
                </form>

                <div className="auth-footer">
                    Don't have an account? <Link to="/register">Register</Link>
                </div>
            </div>
        </div>
    )
}

// Register Page
const RegisterPage = () => {
    const [formData, setFormData] = useState({
        email: '',
        password: '',
        password_confirm: '',
        first_name: '',
        last_name: ''
    })
    const [error, setError] = useState('')
    const [success, setSuccess] = useState('')
    const [loading, setLoading] = useState(false)
    const { register } = useAuth()
    const navigate = useNavigate()

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value })
    }

    const handleSubmit = async (e) => {
        e.preventDefault()
        setError('')
        setLoading(true)

        try {
            const result = await register(formData)
            if (result.verified) {
                setSuccess('Registration successful! You can now login.')
                setTimeout(() => navigate('/login'), 2000)
            } else {
                setSuccess('Registration successful! Please check your email for verification.')
            }
        } catch (err) {
            const errors = err.response?.data
            if (errors) {
                const firstError = Object.values(errors)[0]
                setError(Array.isArray(firstError) ? firstError[0] : firstError)
            } else {
                setError('Registration failed')
            }
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="auth-container fade-in">
            <div className="card auth-card">
                <div className="auth-header">
                    <div className="auth-icon">✨</div>
                    <h2>Create Account</h2>
                    <p>Start encrypting your PDFs securely</p>
                </div>

                {error && <div className="alert alert-error">⚠️ {error}</div>}
                {success && <div className="alert alert-success">✓ {success}</div>}

                <form onSubmit={handleSubmit}>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                        <div className="form-group">
                            <label className="form-label">First Name</label>
                            <input
                                type="text"
                                name="first_name"
                                className="form-input"
                                value={formData.first_name}
                                onChange={handleChange}
                            />
                        </div>
                        <div className="form-group">
                            <label className="form-label">Last Name</label>
                            <input
                                type="text"
                                name="last_name"
                                className="form-input"
                                value={formData.last_name}
                                onChange={handleChange}
                            />
                        </div>
                    </div>

                    <div className="form-group">
                        <label className="form-label">Email</label>
                        <input
                            type="email"
                            name="email"
                            className="form-input"
                            placeholder="you@example.com"
                            value={formData.email}
                            onChange={handleChange}
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label className="form-label">Password</label>
                        <input
                            type="password"
                            name="password"
                            className="form-input"
                            placeholder="Min 8 characters"
                            value={formData.password}
                            onChange={handleChange}
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label className="form-label">Confirm Password</label>
                        <input
                            type="password"
                            name="password_confirm"
                            className="form-input"
                            placeholder="••••••••"
                            value={formData.password_confirm}
                            onChange={handleChange}
                            required
                        />
                    </div>

                    <button type="submit" className="btn btn-primary btn-lg" style={{ width: '100%' }} disabled={loading}>
                        {loading ? 'Creating Account...' : 'Create Account'}
                    </button>
                </form>

                <div className="auth-footer">
                    Already have an account? <Link to="/login">Sign In</Link>
                </div>
            </div>
        </div>
    )
}

// Dashboard Page
const DashboardPage = () => {
    const { user } = useAuth()
    const [file, setFile] = useState(null)
    const [receiverEmail, setReceiverEmail] = useState('')
    const [loading, setLoading] = useState(false)
    const [progress, setProgress] = useState(0)
    const [result, setResult] = useState(null)
    const [error, setError] = useState('')
    const [history, setHistory] = useState([])
    const [dragOver, setDragOver] = useState(false)

    const [viewMode, setViewMode] = useState('encrypted') // 'original', 'chunked', 'shuffled', 'encrypted'
    const [page, setPage] = useState(0) // Start at page 0 (index)

    useEffect(() => {
        fetchHistory()
    }, [])

    const fetchHistory = async () => {
        try {
            const res = await axios.get('/encryption/history/')
            setHistory(res.data)
        } catch (err) {
            console.error('Failed to fetch history')
        }
    }

    const handleDrop = (e) => {
        e.preventDefault()
        setDragOver(false)
        const droppedFile = e.dataTransfer.files[0]
        if (droppedFile && droppedFile.type === 'application/pdf') {
            setFile(droppedFile)
        }
    }

    const handleFileChange = (e) => {
        setFile(e.target.files[0])
    }

    const handleEncrypt = async (e) => {
        e.preventDefault()
        if (!file || !receiverEmail) return

        setLoading(true)
        setError('')
        setResult(null)
        setProgress(0)
        setViewMode('encrypted')
        setPage(0)

        const formData = new FormData()
        formData.append('pdf_file', file)
        formData.append('receiver_email', receiverEmail)
        formData.append('send_email', true)

        // Simulate progress steps
        const progressSteps = [10, 25, 45, 65, 80, 95]
        let stepIndex = 0
        const progressInterval = setInterval(() => {
            if (stepIndex < progressSteps.length) {
                setProgress(progressSteps[stepIndex])
                stepIndex++
            }
        }, 500)

        try {
            const res = await axios.post('/encryption/encrypt/', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            })

            clearInterval(progressInterval)
            setProgress(100)
            setResult(res.data)
            fetchHistory()
        } catch (err) {
            clearInterval(progressInterval)
            clearInterval(progressInterval)
            if (err.response?.data) {
                // Handle different error formats
                const data = err.response.data
                if (data.error) {
                    setError(data.error)
                } else {
                    // Handle validation errors (e.g. {pdf_file: ['Error']})
                    const firstError = Object.values(data)[0]
                    setError(Array.isArray(firstError) ? firstError[0] : (typeof firstError === 'string' ? firstError : 'Encryption failed'))
                }
            } else {
                setError('Encryption failed. Please check server logs.')
            }
        } finally {
            setLoading(false)
        }
    }

    const steps = [
        { label: 'Upload', active: progress >= 0 },
        { label: 'Convert', active: progress >= 25 },
        { label: 'Chunk', active: progress >= 45 },
        { label: 'Shuffle', active: progress >= 65 },
        { label: 'Encrypt', active: progress >= 80 },
        { label: 'Send', active: progress >= 95 }
    ]

    return (
        <div className="dashboard container fade-in">
            <div className="dashboard-header">
                <div>
                    <h1>Dashboard</h1>
                    <p>Welcome, {user?.first_name || user?.email}</p>
                </div>
            </div>

            <div className="dashboard-grid">
                <div className="card">
                    <h3 style={{ marginBottom: '1.5rem' }}>🔐 Encrypt PDF</h3>

                    {error && <div className="alert alert-error">⚠️ {error}</div>}

                    {result ? (
                        <div className="fade-in">
                            <div className="alert alert-success">
                                ✓ PDF encrypted and {result.email_sent ? 'sent' : 'ready'} successfully!
                            </div>

                            <div className="key-display">
                                <div className="key-label">⚠️ Decryption Key (Share with receiver)</div>
                                <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                                    <div className="key-value" style={{ flex: 1 }}>{result.decryption_key}</div>
                                    <button
                                        className="btn btn-secondary"
                                        style={{ padding: '0.5rem', minWidth: 'auto' }}
                                        onClick={() => {
                                            navigator.clipboard.writeText(result.decryption_key);
                                            alert('Key copied to clipboard!');
                                        }}
                                        title="Copy to clipboard"
                                    >
                                        📋
                                    </button>
                                </div>
                            </div>

                            {/* Visualization Controls */}
                            <div style={{ marginTop: '1.5rem' }}>
                                {/* Page Selector */}
                                {result.previews && Array.isArray(result.previews) && result.previews.length > 1 && (
                                    <div style={{
                                        display: 'flex',
                                        justifyContent: 'center',
                                        alignItems: 'center',
                                        gap: '0.5rem',
                                        marginBottom: '1rem'
                                    }}>
                                        <label style={{ fontWeight: 'bold' }}>Page:</label>
                                        <div style={{ display: 'flex', gap: '0.25rem' }}>
                                            {result.previews.map((p, idx) => (
                                                <button
                                                    key={idx}
                                                    onClick={() => setPage(idx)}
                                                    style={{
                                                        padding: '0.25rem 0.75rem',
                                                        border: page === idx ? '2px solid #4f46e5' : '1px solid #ddd',
                                                        borderRadius: '4px',
                                                        background: page === idx ? '#4f46e5' : 'white',
                                                        color: page === idx ? 'white' : '#666',
                                                        cursor: 'pointer'
                                                    }}
                                                >
                                                    {idx + 1}
                                                </button>
                                            ))}
                                        </div>
                                    </div>
                                )}

                                <div className="view-controls" style={{
                                    display: 'flex',
                                    gap: '0.5rem',
                                    marginBottom: '1rem',
                                    justifyContent: 'center'
                                }}>
                                    {[
                                        { id: 'original', icon: '📄', label: 'Original' },
                                        { id: 'chunked', icon: '🧩', label: 'Chunked' },
                                        { id: 'shuffled', icon: '🔀', label: 'Shuffled' },
                                        { id: 'encrypted', icon: '🔐', label: 'Encrypted' },
                                    ].map(mode => (
                                        <button
                                            key={mode.id}
                                            onClick={() => setViewMode(mode.id)}
                                            style={{
                                                padding: '0.5rem 1rem',
                                                border: viewMode === mode.id ? '2px solid #4f46e5' : '1px solid #ddd',
                                                borderRadius: '6px',
                                                background: viewMode === mode.id ? '#eef2ff' : 'white',
                                                color: viewMode === mode.id ? '#4f46e5' : '#666',
                                                cursor: 'pointer',
                                                fontWeight: viewMode === mode.id ? '600' : '400',
                                                transition: 'all 0.2s',
                                                display: 'flex',
                                                alignItems: 'center',
                                                gap: '0.5rem'
                                            }}
                                        >
                                            <span>{mode.icon}</span>
                                            {mode.label}
                                        </button>
                                    ))}
                                </div>

                                <div style={{ textAlign: 'center' }}>
                                    <p style={{ fontSize: '0.9rem', color: '#666', marginBottom: '0.5rem' }}>
                                        {viewMode === 'original' && 'Original page converted to image.'}
                                        {viewMode === 'chunked' && 'Image separated into distinct 32-pixel processing chunks.'}
                                        {viewMode === 'shuffled' && 'Chunks reshuffled using chaos key.'}
                                        {viewMode === 'encrypted' && 'Final DCKP-ES encrypted noise pattern.'}
                                    </p>

                                    {result.previews && (Array.isArray(result.previews) ? result.previews[page] : result.previews)[viewMode] ? (
                                        <img
                                            src={(Array.isArray(result.previews) ? result.previews[page] : result.previews)[viewMode]}
                                            alt={`${viewMode} View`}
                                            style={{
                                                width: '100%',
                                                maxHeight: '400px',
                                                objectFit: 'contain',
                                                borderRadius: '8px',
                                                border: '2px solid #ddd',
                                                boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                                            }}
                                        />
                                    ) : (
                                        <div style={{
                                            padding: '2rem',
                                            background: '#f8fafc',
                                            borderRadius: '8px',
                                            border: '2px dashed #ddd',
                                            color: '#94a3b8'
                                        }}>
                                            Preview not available for this stage
                                        </div>
                                    )}
                                </div>
                            </div>

                            <p style={{ marginTop: '1rem' }}>
                                <strong>Pages:</strong> {result.num_pages} |
                                <strong> Sent to:</strong> {receiverEmail}
                            </p>

                            <a
                                href={`/api/encryption/download/${result.encrypted_file}`}
                                className="btn btn-secondary"
                                style={{ marginTop: '0.5rem', display: 'inline-block', textDecoration: 'none' }}
                                download
                            >
                                📥 Download Encrypted File (.png)
                            </a>

                            <button
                                className="btn btn-primary"
                                style={{ marginTop: '1rem' }}
                                onClick={() => {
                                    setResult(null)
                                    setFile(null)
                                    setReceiverEmail('')
                                    setProgress(0)
                                }}
                            >
                                Encrypt Another
                            </button>
                        </div>
                    ) : (
                        <form onSubmit={handleEncrypt}>
                            <div
                                className={`upload-zone ${dragOver ? 'dragover' : ''} ${file ? 'has-file' : ''}`}
                                onDrop={handleDrop}
                                onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
                                onDragLeave={() => setDragOver(false)}
                                onClick={() => document.getElementById('file-input').click()}
                            >
                                <input
                                    id="file-input"
                                    type="file"
                                    accept=".pdf"
                                    onChange={handleFileChange}
                                    style={{ display: 'none' }}
                                />
                                <div className="upload-icon">{file ? '✅' : '📄'}</div>
                                <div className="upload-text">
                                    {file ? file.name : 'Drop PDF here or click to browse'}
                                </div>
                                <div className="upload-hint">
                                    {file ? `${(file.size / 1024 / 1024).toFixed(2)} MB` : 'Max file size: 50MB'}
                                </div>
                            </div>

                            <div className="form-group" style={{ marginTop: '1.5rem' }}>
                                <label className="form-label">Receiver's Email</label>
                                <input
                                    type="email"
                                    className="form-input"
                                    placeholder="receiver@example.com"
                                    value={receiverEmail}
                                    onChange={(e) => setReceiverEmail(e.target.value)}
                                    required
                                />
                            </div>

                            {loading && (
                                <div className="progress-container">
                                    <div className="progress-bar">
                                        <div className="progress-fill" style={{ width: `${progress}%` }}></div>
                                    </div>
                                    <div className="progress-steps">
                                        {steps.map((step, i) => (
                                            <div key={i} className="progress-step">
                                                <div className={`step-circle ${step.active ? 'active' : ''}`}>
                                                    {i + 1}
                                                </div>
                                                <span className="step-label">{step.label}</span>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}

                            <button
                                type="submit"
                                className="btn btn-primary btn-lg"
                                style={{ width: '100%', marginTop: '1rem' }}
                                disabled={!file || !receiverEmail || loading}
                            >
                                {loading ? 'Encrypting...' : '🔐 Encrypt & Send'}
                            </button>
                        </form>
                    )}
                </div>

                <div className="card">
                    <h3 style={{ marginBottom: '1.5rem' }}>📜 Recent Transfers</h3>

                    {history.length === 0 ? (
                        <p style={{ textAlign: 'center', padding: '2rem' }}>No transfers yet</p>
                    ) : (
                        <table className="history-table">
                            <thead>
                                <tr>
                                    <th>Receiver</th>
                                    <th>Date</th>
                                </tr>
                            </thead>
                            <tbody>
                                {history.slice(0, 10).map((transfer, i) => (
                                    <tr key={i}>
                                        <td>{transfer.receiver_email}</td>
                                        <td>{new Date(transfer.timestamp).toLocaleDateString()}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}
                </div>
            </div>
        </div>
    )
}

// Decrypt Page
const DecryptPage = () => {
    const [file, setFile] = useState(null)
    const [decryptionKey, setDecryptionKey] = useState('')
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')
    const [dragOver, setDragOver] = useState(false)

    const handleDrop = (e) => {
        e.preventDefault()
        setDragOver(false)
        const droppedFile = e.dataTransfer.files[0]
        if (droppedFile && droppedFile.name.endsWith('.png')) {
            setFile(droppedFile)
        }
    }

    const handleDecrypt = async (e) => {
        e.preventDefault()
        if (!file || !decryptionKey) return

        setLoading(true)
        setError('')

        const formData = new FormData()
        formData.append('encrypted_file', file)
        formData.append('decryption_key', decryptionKey)

        try {
            const res = await axios.post('/encryption/decrypt/', formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
                responseType: 'blob'
            })

            // Download the decrypted PDF
            const url = window.URL.createObjectURL(new Blob([res.data]))
            const link = document.createElement('a')
            link.href = url
            link.setAttribute('download', 'decrypted.pdf')
            document.body.appendChild(link)
            link.click()
            link.remove()
            window.URL.revokeObjectURL(url)

        } catch (err) {
            if (err.response?.data instanceof Blob) {
                const text = await err.response.data.text()
                try {
                    const json = JSON.parse(text)
                    setError(json.error || 'Decryption failed')
                } catch {
                    setError('Decryption failed')
                }
            } else {
                setError(err.response?.data?.error || 'Decryption failed')
            }
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="auth-container fade-in">
            <div className="card" style={{ maxWidth: '500px', width: '100%' }}>
                <div className="auth-header">
                    <div className="auth-icon">🔓</div>
                    <h2>Decrypt PDF</h2>
                    <p>Enter your decryption key to unlock the file</p>
                </div>

                {error && <div className="alert alert-error">⚠️ {error}</div>}

                <form onSubmit={handleDecrypt}>
                    <div
                        className={`upload-zone ${dragOver ? 'dragover' : ''} ${file ? 'has-file' : ''}`}
                        onDrop={handleDrop}
                        onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
                        onDragLeave={() => setDragOver(false)}
                        onClick={() => document.getElementById('enc-file-input').click()}
                    >
                        <input
                            id="enc-file-input"
                            type="file"
                            accept="*"
                            onChange={(e) => setFile(e.target.files[0])}
                            style={{ display: 'none' }}
                        />
                        <div className="upload-icon">{file ? '✅' : '📦'}</div>
                        <div className="upload-text">
                            {file ? file.name : 'Drop encrypted file here'}
                        </div>
                        <div className="upload-hint">.png file from email / gallery</div>
                    </div>

                    <div className="form-group" style={{ marginTop: '1.5rem' }}>
                        <label className="form-label">Decryption Key</label>
                        <input
                            type="text"
                            className="form-input"
                            placeholder="filename.pdf|2024-01-01T12:00:00"
                            value={decryptionKey}
                            onChange={(e) => setDecryptionKey(e.target.value)}
                            required
                        />
                    </div>

                    <button
                        type="submit"
                        className="btn btn-primary btn-lg"
                        style={{ width: '100%' }}
                        disabled={!file || !decryptionKey || loading}
                    >
                        {loading ? 'Decrypting...' : '🔓 Decrypt & Download'}
                    </button>
                </form>

                <div className="alert alert-info" style={{ marginTop: '1.5rem' }}>
                    ℹ️ The decryption key was sent in the email along with the encrypted file.
                </div>
            </div>
        </div>
    )
}

// Footer
const Footer = () => (
    <footer className="footer">
        <p>© 2024 PDF Encryption System | Powered by DCKP-ES Algorithm</p>
    </footer>
)

// Main App
function App() {
    return (
        <BrowserRouter>
            <AuthProvider>
                <div className="app">
                    <Navbar />
                    <Routes>
                        <Route path="/" element={<HomePage />} />
                        <Route path="/login" element={<LoginPage />} />
                        <Route path="/register" element={<RegisterPage />} />
                        <Route path="/decrypt" element={<DecryptPage />} />
                        <Route path="/dashboard" element={
                            <ProtectedRoute>
                                <DashboardPage />
                            </ProtectedRoute>
                        } />
                    </Routes>
                    <Footer />
                </div>
            </AuthProvider>
        </BrowserRouter>
    )
}

export default App
