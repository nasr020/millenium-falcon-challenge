import React, { useState } from "react";
import { Upload, AlertCircle, CheckCircle2, XCircle } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "./components/ui/alert";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "./components/ui/card";

const App = () => {
  const [odds, setOdds] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [fileName, setFileName] = useState("");

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    // Reset states
    setError(null);
    setOdds(null);
    setLoading(true);
    setFileName(file.name);

    // Validate file type
    if (!file.name.endsWith(".json")) {
      setError("Please upload a JSON file");
      setLoading(false);
      return;
    }

    // Create form data
    const formData = new FormData();
    formData.append("empire_file", file);

    try {
      const response = await fetch("http://localhost:8000/api/v1/odds/", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setOdds(data.odds);
    } catch (error) {
      setError("Failed to compute odds. Please try again.");
      console.error("Error:", error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = () => {
    if (odds === null) return "bg-gray-100";
    if (odds === 0) return "bg-red-100";
    if (odds === 100) return "bg-green-100";
    return "bg-yellow-100";
  };

  const getStatusIcon = () => {
    if (odds === 0) return <XCircle className="h-6 w-6 text-red-600" />;
    if (odds === 100)
      return <CheckCircle2 className="h-6 w-6 text-green-600" />;
    return <AlertCircle className="h-6 w-6 text-yellow-600" />;
  };

  const getStatusMessage = () => {
    if (odds === 0) return "The Millennium Falcon cannot reach Endor in time";
    if (odds === 100) return "The Millennium Falcon can reach Endor safely!";
    return "The Millennium Falcon might encounter bounty hunters";
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-2xl mx-auto space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>Millennium Falcon Odds Calculator</CardTitle>
            <CardDescription>
              Upload Empire intelligence data to calculate survival odds
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-center w-full">
                <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100">
                  <div className="flex flex-col items-center justify-center pt-5 pb-6">
                    <Upload className="h-8 w-8 text-gray-500 mb-2" />
                    <p className="mb-2 text-sm text-gray-500">
                      <span className="font-semibold">Click to upload</span> or
                      drag and drop
                    </p>
                    <p className="text-xs text-gray-500">.json files only</p>
                    {fileName && (
                      <p className="text-sm text-gray-700 mt-2">
                        Selected: {fileName}
                      </p>
                    )}
                  </div>
                  <input
                    type="file"
                    className="hidden"
                    accept=".json"
                    onChange={handleFileUpload}
                  />
                </label>
              </div>

              {loading && (
                <div className="text-center py-4">
                  <div className="animate-pulse">Computing odds...</div>
                </div>
              )}

              {error && (
                <Alert variant="destructive">
                  <AlertCircle className="h-4 w-4" />
                  <AlertTitle>Error</AlertTitle>
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}

              {odds !== null && !error && (
                <div
                  className={`p-6 rounded-lg ${getStatusColor()} transition-all`}
                >
                  <div className="flex items-center space-x-3">
                    {getStatusIcon()}
                    <div>
                      <h3 className="text-lg font-semibold">
                        {odds}% Success Rate
                      </h3>
                      <p className="text-sm text-gray-600">
                        {getStatusMessage()}
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default App;
