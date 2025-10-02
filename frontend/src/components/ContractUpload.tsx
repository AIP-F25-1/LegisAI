import { useState, useCallback } from "react";
import { ArrowLeft, Upload, FileText, Check, AlertCircle, Download } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Label } from "@/components/ui/label";
import { Progress } from "@/components/ui/progress";
import { useToast } from "@/hooks/use-toast";
import logo from "@/assets/logo.png";

interface ContractUploadProps {
  onBack: () => void;
}

type OutputType = "draft" | "summarize" | "regularize";
type UploadStatus = "idle" | "uploading" | "processing" | "completed" | "error";

const ContractUpload = ({ onBack }: ContractUploadProps) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [outputType, setOutputType] = useState<OutputType>("summarize");
  const [uploadStatus, setUploadStatus] = useState<UploadStatus>("idle");
  const [progress, setProgress] = useState(0);
  const [dragActive, setDragActive] = useState(false);
  const { toast } = useToast();

  const outputOptions = [
    {
      value: "draft" as OutputType,
      title: "Draft Contract",
      description: "Generate a preliminary draft based on your document"
    },
    {
      value: "summarize" as OutputType,
      title: "Contract Summary", 
      description: "Create a concise summary of key terms and clauses"
    },
    {
      value: "regularize" as OutputType,
      title: "Regularized Contract",
      description: "Standardize formatting and language to industry norms"
    }
  ];

  const handleFileSelect = useCallback((files: FileList | null) => {
    if (files && files[0]) {
      const file = files[0];
      if (file.type === "application/pdf" || file.name.endsWith('.pdf')) {
        setSelectedFile(file);
        setUploadStatus("idle");
        toast({
          title: "File selected",
          description: `Selected: ${file.name}`,
        });
      } else {
        toast({
          title: "Invalid file type",
          description: "Please upload a PDF file only",
          variant: "destructive",
        });
      }
    }
  }, [toast]);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    handleFileSelect(e.dataTransfer.files);
  }, [handleFileSelect]);

  const handleUpload = async () => {
    if (!selectedFile) return;

    setUploadStatus("uploading");
    setProgress(0);

    // Simulate upload progress
    const uploadInterval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 90) {
          clearInterval(uploadInterval);
          setUploadStatus("processing");
          
          // Simulate processing time
          setTimeout(() => {
            setUploadStatus("completed");
            setProgress(100);
            toast({
              title: "Contract processing completed!",
              description: `Your ${outputOptions.find(opt => opt.value === outputType)?.title.toLowerCase()} is ready for download.`,
            });
          }, 3000);
          
          return 90;
        }
        return prev + Math.random() * 15;
      });
    }, 200);
  };

  const handleDownload = () => {
    // Simulate file download
    const outputFileName = `${selectedFile?.name.replace('.pdf', '')}_${outputType}.pdf`;
    toast({
      title: "Download started",
      description: `Downloading ${outputFileName}...`,
    });
  };

  const getStatusIcon = () => {
    switch (uploadStatus) {
      case "completed":
        return <Check className="h-5 w-5 text-success" />;
      case "error":
        return <AlertCircle className="h-5 w-5 text-destructive" />;
      default:
        return <FileText className="h-5 w-5 text-muted-foreground" />;
    }
  };

  const getStatusText = () => {
    switch (uploadStatus) {
      case "uploading":
        return "Uploading file...";
      case "processing":
        return `Processing contract for ${outputOptions.find(opt => opt.value === outputType)?.title.toLowerCase()}...`;
      case "completed":
        return "Contract processing completed successfully!";
      case "error":
        return "Error processing contract. Please try again.";
      default:
        return "Ready to upload";
    }
  };

  return (
    <div className="min-h-screen bg-gradient-subtle">
      <div className="container mx-auto px-4 py-6 max-w-4xl">
        {/* Header */}
        <Card className="mb-6 border-0 bg-gradient-card shadow-soft">
          <CardHeader className="pb-4">
            <div className="flex items-center justify-between">
              <Button
                variant="ghost"
                onClick={onBack}
                className="hover:bg-secondary/80"
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Main
              </Button>
              <div className="flex items-center space-x-3">
                <img src={logo} alt="Logo" className="h-8 w-auto" />
                <div>
                  <h2 className="text-xl font-semibold text-foreground">Contract Processing</h2>
                  <p className="text-sm text-muted-foreground">Upload and analyze your legal documents</p>
                </div>
              </div>
            </div>
          </CardHeader>
        </Card>

        <div className="grid lg:grid-cols-2 gap-6">
          {/* Upload Section */}
          <Card className="border-0 bg-card shadow-medium">
            <CardHeader>
              <CardTitle className="flex items-center">
                <Upload className="h-5 w-5 mr-2 text-primary" />
                Upload Contract
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* File Drop Zone */}
              <div
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
                className={`border-2 border-dashed rounded-lg p-8 text-center transition-all duration-300 ${
                  dragActive
                    ? "border-primary bg-primary/5"
                    : selectedFile
                    ? "border-success bg-success/5"
                    : "border-border hover:border-primary/50"
                }`}
              >
                <div className="flex flex-col items-center space-y-4">
                  {getStatusIcon()}
                  {selectedFile ? (
                    <div>
                      <p className="font-medium text-foreground">{selectedFile.name}</p>
                      <p className="text-sm text-muted-foreground">
                        {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
                      </p>
                    </div>
                  ) : (
                    <div>
                      <p className="font-medium text-foreground">Drop your contract here</p>
                      <p className="text-sm text-muted-foreground">or click to browse files</p>
                    </div>
                  )}
                  <input
                    type="file"
                    accept=".pdf"
                    onChange={(e) => handleFileSelect(e.target.files)}
                    className="hidden"
                    id="file-upload"
                  />
                  <Label htmlFor="file-upload" className="cursor-pointer">
                    <Button variant="outline" className="mt-2">
                      {selectedFile ? "Change File" : "Select File"}
                    </Button>
                  </Label>
                  <p className="text-xs text-muted-foreground">PDF files only • Max 20MB</p>
                </div>
              </div>

              {/* Upload Progress */}
              {(uploadStatus === "uploading" || uploadStatus === "processing") && (
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-foreground">{getStatusText()}</span>
                    <span className="text-muted-foreground">{Math.round(progress)}%</span>
                  </div>
                  <Progress value={progress} className="h-2" />
                </div>
              )}

              {/* Success Message */}
              {uploadStatus === "completed" && (
                <div className="bg-success/10 border border-success/20 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center">
                      <Check className="h-5 w-5 text-success mr-2" />
                      <div>
                        <p className="font-medium text-success">Processing Complete!</p>
                        <p className="text-sm text-success/80">{getStatusText()}</p>
                      </div>
                    </div>
                    <Button onClick={handleDownload} className="bg-success hover:bg-success/90">
                      <Download className="h-4 w-4 mr-2" />
                      Download
                    </Button>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Output Options */}
          <Card className="border-0 bg-card shadow-medium">
            <CardHeader>
              <CardTitle className="flex items-center">
                <FileText className="h-5 w-5 mr-2 text-accent" />
                Output Format
              </CardTitle>
            </CardHeader>
            <CardContent>
              <RadioGroup
                value={outputType}
                onValueChange={(value: OutputType) => setOutputType(value)}
                className="space-y-4"
              >
                {outputOptions.map((option) => (
                  <div
                    key={option.value}
                    className={`flex items-start space-x-3 p-4 rounded-lg border transition-all duration-200 ${
                      outputType === option.value
                        ? "border-primary bg-primary/5"
                        : "border-border hover:border-primary/30"
                    }`}
                  >
                    <RadioGroupItem
                      value={option.value}
                      id={option.value}
                      className="mt-1"
                    />
                    <div className="flex-1">
                      <Label
                        htmlFor={option.value}
                        className="font-medium text-foreground cursor-pointer"
                      >
                        {option.title}
                      </Label>
                      <p className="text-sm text-muted-foreground mt-1">
                        {option.description}
                      </p>
                    </div>
                  </div>
                ))}
              </RadioGroup>

              {/* Process Button */}
              <Button
                onClick={handleUpload}
                disabled={!selectedFile || uploadStatus === "uploading" || uploadStatus === "processing"}
                className="w-full mt-6 bg-gradient-primary hover:shadow-medium py-3"
                size="lg"
              >
                {uploadStatus === "uploading" || uploadStatus === "processing" ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin mr-2" />
                    Processing...
                  </>
                ) : uploadStatus === "completed" ? (
                  <>
                    <Check className="h-4 w-4 mr-2" />
                    Completed
                  </>
                ) : (
                  <>
                    <Upload className="h-4 w-4 mr-2" />
                    Process Contract
                  </>
                )}
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default ContractUpload;