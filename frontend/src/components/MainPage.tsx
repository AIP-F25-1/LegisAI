import { MessageSquare, Upload, FileText, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import logo from "@/assets/logo.png";

interface MainPageProps {
  onNavigate: (page: 'chatbot' | 'upload') => void;
}

const MainPage = ({ onNavigate }: MainPageProps) => {
  return (
    <div className="min-h-screen bg-gradient-subtle">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <header className="text-center mb-12">
          <div className="flex justify-center mb-6">
            <img src={logo} alt="LegalTech Pro" className="h-16 w-auto" />
          </div>
          <h1 className="text-4xl font-bold text-foreground mb-4">
            Legal Document Assistant
          </h1>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Streamline your legal workflow with AI-powered contract processing and intelligent chat assistance
          </p>
        </header>

        {/* Main Actions */}
        <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
          {/* Chatbot Card */}
          <Card 
            className="group hover:shadow-large transition-all duration-300 cursor-pointer border-0 bg-gradient-card"
            onClick={() => onNavigate('chatbot')}
          >
            <CardContent className="p-8 text-center">
              <div className="mb-6 flex justify-center">
                <div className="p-4 rounded-full bg-primary/10 group-hover:bg-primary/20 transition-colors">
                  <MessageSquare className="h-12 w-12 text-primary" />
                </div>
              </div>
              <h3 className="text-2xl font-semibold mb-4 text-card-foreground">
                AI Legal Assistant
              </h3>
              <p className="text-muted-foreground mb-6 leading-relaxed">
                Get instant answers to legal questions, contract guidance, and professional advice from our AI assistant
              </p>
              <Button 
                className="bg-gradient-primary hover:shadow-medium transition-all duration-300 px-8 py-3 text-base font-medium"
                size="lg"
              >
                Start Chatting
                <Sparkles className="ml-2 h-4 w-4" />
              </Button>
            </CardContent>
          </Card>

          {/* Contract Upload Card */}
          <Card 
            className="group hover:shadow-large transition-all duration-300 cursor-pointer border-0 bg-gradient-card"
            onClick={() => onNavigate('upload')}
          >
            <CardContent className="p-8 text-center">
              <div className="mb-6 flex justify-center">
                <div className="p-4 rounded-full bg-accent/10 group-hover:bg-accent/20 transition-colors">
                  <Upload className="h-12 w-12 text-accent" />
                </div>
              </div>
              <h3 className="text-2xl font-semibold mb-4 text-card-foreground">
                Contract Processing
              </h3>
              <p className="text-muted-foreground mb-6 leading-relaxed">
                Upload contracts for AI-powered analysis, summarization, and standardization with multiple output formats
              </p>
              <Button 
                variant="outline" 
                className="border-accent text-accent hover:bg-accent hover:text-accent-foreground px-8 py-3 text-base font-medium transition-all duration-300"
                size="lg"
              >
                Upload Contract
                <FileText className="ml-2 h-4 w-4" />
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Features Overview */}
        <div className="mt-16 text-center">
          <h2 className="text-2xl font-semibold mb-8 text-foreground">
            Powerful Features at Your Fingertips
          </h2>
          <div className="grid md:grid-cols-3 gap-6 max-w-3xl mx-auto">
            <div className="p-4">
              <div className="w-12 h-12 bg-primary/10 rounded-lg mx-auto mb-3 flex items-center justify-center">
                <MessageSquare className="h-6 w-6 text-primary" />
              </div>
              <h4 className="font-medium text-foreground">AI Chat Support</h4>
              <p className="text-sm text-muted-foreground mt-1">24/7 legal guidance</p>
            </div>
            <div className="p-4">
              <div className="w-12 h-12 bg-accent/10 rounded-lg mx-auto mb-3 flex items-center justify-center">
                <FileText className="h-6 w-6 text-accent" />
              </div>
              <h4 className="font-medium text-foreground">Smart Processing</h4>
              <p className="text-sm text-muted-foreground mt-1">Automated analysis</p>
            </div>
            <div className="p-4">
              <div className="w-12 h-12 bg-success/10 rounded-lg mx-auto mb-3 flex items-center justify-center">
                <Sparkles className="h-6 w-6 text-success" />
              </div>
              <h4 className="font-medium text-foreground">Multiple Formats</h4>
              <p className="text-sm text-muted-foreground mt-1">Draft, summary, standard</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MainPage;