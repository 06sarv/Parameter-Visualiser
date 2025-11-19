import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar, Line, Pie } from 'react-chartjs-2';
import './App.css';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

const API_BASE_URL = 'http://localhost:8000/api';

function App() {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState({ text: '', type: '' });
  const [currentDataset, setCurrentDataset] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/history/`);
      setHistory(response.data);
    } catch (error) {
      console.error('Error fetching history:', error);
    }
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      if (selectedFile.name.endsWith('.csv')) {
        setFile(selectedFile);
        setMessage({ text: '', type: '' });
      } else {
        setMessage({ text: 'Please select a CSV file', type: 'error' });
        setFile(null);
      }
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setMessage({ text: 'Please select a file first', type: 'error' });
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    setUploading(true);
    setMessage({ text: '', type: '' });

    try {
      const response = await axios.post(`${API_BASE_URL}/datasets/upload_csv/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setCurrentDataset(response.data);
      setMessage({ text: 'File uploaded successfully!', type: 'success' });
      setFile(null);
      fetchHistory();
    } catch (error) {
      const errorMsg = error.response?.data?.error || 'Error uploading file';
      setMessage({ text: errorMsg, type: 'error' });
    } finally {
      setUploading(false);
    }
  };

  const loadDataset = async (datasetId) => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_BASE_URL}/datasets/${datasetId}/`);
      setCurrentDataset(response.data);
      setMessage({ text: 'Dataset loaded successfully!', type: 'success' });
    } catch (error) {
      setMessage({ text: 'Error loading dataset', type: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const downloadPDF = async () => {
    if (!currentDataset) return;

    try {
      const response = await axios.get(
        `${API_BASE_URL}/datasets/${currentDataset.id}/generate_pdf/`,
        { responseType: 'blob' }
      );

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `equipment_report_${currentDataset.id}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      setMessage({ text: 'PDF downloaded successfully!', type: 'success' });
    } catch (error) {
      setMessage({ text: 'Error generating PDF', type: 'error' });
    }
  };

  // Prepare chart data
  const getTypeDistributionData = () => {
    if (!currentDataset?.equipment_types) return null;

    const types = Object.keys(currentDataset.equipment_types);
    const counts = Object.values(currentDataset.equipment_types);

    return {
      labels: types,
      datasets: [
        {
          label: 'Equipment Count',
          data: counts,
          backgroundColor: [
            'rgba(102, 126, 234, 0.8)',
            'rgba(118, 75, 162, 0.8)',
            'rgba(72, 187, 120, 0.8)',
            'rgba(237, 137, 54, 0.8)',
            'rgba(229, 62, 62, 0.8)',
            'rgba(49, 151, 149, 0.8)',
          ],
          borderColor: '#ffffff',
          borderWidth: 2,
        },
      ],
    };
  };

  const getParameterComparisonData = () => {
    if (!currentDataset?.equipment_items) return null;

    const items = currentDataset.equipment_items.slice(0, 10); // First 10 items

    return {
      labels: items.map(item => item.equipment_name.substring(0, 15)),
      datasets: [
        {
          label: 'Flowrate',
          data: items.map(item => item.flowrate),
          borderColor: 'rgb(102, 126, 234)',
          backgroundColor: 'rgba(102, 126, 234, 0.1)',
          borderWidth: 2,
        },
        {
          label: 'Pressure',
          data: items.map(item => item.pressure),
          borderColor: 'rgb(118, 75, 162)',
          backgroundColor: 'rgba(118, 75, 162, 0.1)',
          borderWidth: 2,
        },
        {
          label: 'Temperature',
          data: items.map(item => item.temperature),
          borderColor: 'rgb(72, 187, 120)',
          backgroundColor: 'rgba(72, 187, 120, 0.1)',
          borderWidth: 2,
        },
      ],
    };
  };

  const getAveragesData = () => {
    if (!currentDataset) return null;

    return {
      labels: ['Flowrate', 'Pressure', 'Temperature'],
      datasets: [
        {
          label: 'Average Values',
          data: [
            currentDataset.avg_flowrate,
            currentDataset.avg_pressure,
            currentDataset.avg_temperature,
          ],
          backgroundColor: [
            'rgba(102, 126, 234, 0.8)',
            'rgba(118, 75, 162, 0.8)',
            'rgba(72, 187, 120, 0.8)',
          ],
          borderColor: [
            'rgb(102, 126, 234)',
            'rgb(118, 75, 162)',
            'rgb(72, 187, 120)',
          ],
          borderWidth: 2,
        },
      ],
    };
  };

  return (
    <div className="App">
      <div className="container">
        <div className="header">
          <h1>Chemical Equipment Visualizer</h1>
          <p>Upload and analyze chemical equipment data with interactive visualizations</p>
        </div>

        {/* Upload Section */}
        <div className="card upload-section">
          <h2>Upload CSV File</h2>
          <div className="upload-controls">
            <div className="file-input-wrapper">
              <input
                type="file"
                id="file-input"
                accept=".csv"
                onChange={handleFileChange}
              />
              <label htmlFor="file-input" className="file-input-label">
                Choose File
              </label>
            </div>
            {file && <span className="file-name">Selected: {file.name}</span>}
            <button
              className="upload-button"
              onClick={handleUpload}
              disabled={!file || uploading}
            >
              {uploading ? 'Uploading...' : 'Upload & Analyze'}
            </button>
          </div>
          {message.text && (
            <div className={`message ${message.type}`}>{message.text}</div>
          )}
        </div>

        {/* Current Dataset Summary */}
        {currentDataset && (
          <>
            <div className="card">
              <h2>Dataset: {currentDataset.name}</h2>
              <div className="stats-grid">
                <div className="stat-card">
                  <h3>Total Equipment</h3>
                  <p>{currentDataset.total_count}</p>
                </div>
                <div className="stat-card">
                  <h3>Avg Flowrate</h3>
                  <p>{currentDataset.avg_flowrate.toFixed(2)}</p>
                </div>
                <div className="stat-card">
                  <h3>Avg Pressure</h3>
                  <p>{currentDataset.avg_pressure.toFixed(2)}</p>
                </div>
                <div className="stat-card">
                  <h3>Avg Temperature</h3>
                  <p>{currentDataset.avg_temperature.toFixed(2)}</p>
                </div>
              </div>

              <div className="action-buttons">
                <button className="btn-pdf" onClick={downloadPDF}>
                  Download PDF Report
                </button>
              </div>
            </div>

            {/* Charts Section */}
            <div className="card charts-section">
              <h2>Data Visualizations</h2>
              <div className="charts-grid">
                {getTypeDistributionData() && (
                  <div className="chart-container">
                    <h3>Equipment Type Distribution</h3>
                    <Pie data={getTypeDistributionData()} />
                  </div>
                )}
                {getAveragesData() && (
                  <div className="chart-container">
                    <h3>Average Parameters</h3>
                    <Bar
                      data={getAveragesData()}
                      options={{
                        responsive: true,
                        plugins: {
                          legend: {
                            display: false,
                          },
                        },
                      }}
                    />
                  </div>
                )}
              </div>
              {getParameterComparisonData() && (
                <div className="chart-container" style={{ marginTop: '25px' }}>
                  <h3>Equipment Parameters Comparison (First 10 Items)</h3>
                  <Line
                    data={getParameterComparisonData()}
                    options={{
                      responsive: true,
                      plugins: {
                        legend: {
                          position: 'top',
                        },
                      },
                    }}
                  />
                </div>
              )}
            </div>

            {/* Data Table */}
            <div className="card data-table-section">
              <h2>Equipment Details</h2>
              <div className="table-wrapper">
                <table>
                  <thead>
                    <tr>
                      <th>Equipment Name</th>
                      <th>Type</th>
                      <th>Flowrate</th>
                      <th>Pressure</th>
                      <th>Temperature</th>
                    </tr>
                  </thead>
                  <tbody>
                    {currentDataset.equipment_items.map((item) => (
                      <tr key={item.id}>
                        <td>{item.equipment_name}</td>
                        <td>{item.type}</td>
                        <td>{item.flowrate.toFixed(2)}</td>
                        <td>{item.pressure.toFixed(2)}</td>
                        <td>{item.temperature.toFixed(2)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        )}

        {/* History Section */}
        {history.length > 0 && (
          <div className="card history-section">
            <h2>Recent Uploads (Last 5)</h2>
            <div className="history-list">
              {history.map((dataset) => (
                <div
                  key={dataset.id}
                  className="history-item"
                  onClick={() => loadDataset(dataset.id)}
                >
                  <h3>{dataset.name}</h3>
                  <p>Uploaded: {new Date(dataset.uploaded_at).toLocaleString()}</p>
                  <p>Total Equipment: {dataset.total_count}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {loading && <div className="loading">Loading dataset...</div>}
      </div>
    </div>
  );
}

export default App;
