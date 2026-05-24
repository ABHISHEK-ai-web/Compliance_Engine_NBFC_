import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import { uploadRegulation, uploadPolicy } from '../../services/api';
import RBISyncPanel from './RBISyncPanel';

export default function UploadCenter() {
  const [uploadType, setUploadType] = useState('regulation');
  const [uploads, setUploads] = useState([]);

  const onDrop = useCallback(
    async (acceptedFiles) => {
      for (const file of acceptedFiles) {
        const id = Date.now() + Math.random();
        setUploads((prev) => [
          ...prev,
          { id, name: file.name, progress: 0, status: 'uploading', type: uploadType },
        ]);

        try {
          const uploadFn = uploadType === 'regulation' ? uploadRegulation : uploadPolicy;
          const response = await uploadFn(file, (progress) => {
            setUploads((prev) =>
              prev.map((u) => (u.id === id ? { ...u, progress } : u))
            );
          });
          setUploads((prev) =>
            prev.map((u) =>
              u.id === id
                ? { ...u, status: 'success', progress: 100, result: response.data }
                : u
            )
          );
        } catch (error) {
          setUploads((prev) =>
            prev.map((u) =>
              u.id === id
                ? { ...u, status: 'error', error: error.response?.data?.detail || 'Upload failed' }
                : u
            )
          );
        }
      }
    },
    [uploadType]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'application/pdf': ['.pdf'] },
    multiple: true,
  });

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Document Upload Center</h2>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Upload RBI circulars, internal SOPs, and audit reports for compliance analysis
        </p>
      </div>

      <RBISyncPanel />

      <div className="flex gap-3">
        {['regulation', 'policy', 'audit_report'].map((type) => (
          <button
            key={type}
            onClick={() => setUploadType(type)}
            className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
              uploadType === type
                ? 'bg-primary-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700'
            }`}
          >
            {type === 'regulation' && 'RBI Circular'}
            {type === 'policy' && 'Internal SOP'}
            {type === 'audit_report' && 'Audit Report'}
          </button>
        ))}
      </div>

      <div
        {...getRootProps()}
        className={`cursor-pointer rounded-xl border-2 border-dashed p-12 text-center transition-colors ${
          isDragActive
            ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/10'
            : 'border-gray-300 hover:border-primary-400 dark:border-gray-700 dark:hover:border-primary-600'
        }`}
      >
        <input {...getInputProps()} />
        <Upload className="mx-auto h-12 w-12 text-gray-400 dark:text-gray-500" />
        <p className="mt-4 text-base font-medium text-gray-700 dark:text-gray-300">
          {isDragActive ? 'Drop files here...' : 'Drag & drop PDF files here'}
        </p>
        <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
          or click to browse. Only PDF files accepted.
        </p>
        <p className="mt-1 text-xs text-gray-400 dark:text-gray-500">
          Uploading as: <span className="font-medium text-primary-600 dark:text-primary-400">{uploadType === 'regulation' ? 'RBI Circular' : uploadType === 'policy' ? 'Internal SOP' : 'Audit Report'}</span>
        </p>
      </div>

      {uploads.length > 0 && (
        <div className="space-y-3">
          <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300">Upload History</h3>
          {uploads.map((upload) => (
            <div
              key={upload.id}
              className="flex items-center gap-3 rounded-lg border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-800"
            >
              <FileText className="h-8 w-8 text-gray-400" />
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-800 dark:text-gray-200">{upload.name}</p>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  {upload.type === 'regulation' ? 'RBI Circular' : upload.type === 'policy' ? 'Internal SOP' : 'Audit Report'}
                </p>
                {upload.status === 'uploading' && (
                  <div className="mt-2 h-1.5 w-full rounded-full bg-gray-200 dark:bg-gray-700">
                    <div
                      className="h-1.5 rounded-full bg-primary-600 transition-all"
                      style={{ width: `${upload.progress}%` }}
                    />
                  </div>
                )}
                {upload.result && (
                  <p className="mt-1 text-xs text-success-600 dark:text-success-500">
                    {upload.result.chunks_created} chunks indexed
                  </p>
                )}
                {upload.error && (
                  <p className="mt-1 text-xs text-danger-600 dark:text-danger-500">{upload.error}</p>
                )}
              </div>
              <div>
                {upload.status === 'uploading' && <Loader2 className="h-5 w-5 animate-spin text-primary-500" />}
                {upload.status === 'success' && <CheckCircle className="h-5 w-5 text-success-500" />}
                {upload.status === 'error' && <AlertCircle className="h-5 w-5 text-danger-500" />}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
