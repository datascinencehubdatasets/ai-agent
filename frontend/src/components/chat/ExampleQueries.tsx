interface QueryCardProps {
  title: string;
  description: string;
  onClick: (query: string) => void;
}

const QueryCard = ({ title, description, onClick }: QueryCardProps) => (
  <div 
    className="p-4 bg-white rounded-lg shadow-sm border border-gray-100 cursor-pointer hover:shadow-md transition-shadow"
    onClick={() => onClick(title)}
  >
    <h3 className="font-medium text-gray-900 mb-1">{title}</h3>
    <p className="text-sm text-gray-600">{description}</p>
  </div>
);

interface ExampleQueriesProps {
  onQueryClick: (query: string) => void;
}

export const ExampleQueries = ({ onQueryClick }: ExampleQueriesProps) => {
  const exampleQueries = [
    {
      title: "What is Murabaha financing?",
      description: "Learn about Islamic profit-based financing structure"
    },
    {
      title: "Explain Sukuk investments",
      description: "Discover Islamic alternatives to conventional bonds"
    },
    {
      title: "How does Islamic insurance work?",
      description: "Understanding Takaful and its principles"
    },
    {
      title: "What is Riba?",
      description: "Learn about the prohibition of interest in Islamic finance"
    }
  ];

  return (
    <div className="max-w-3xl mx-auto w-full px-4">
      <div className="text-center mb-8">
        <h1 className="text-2xl font-semibold text-gray-900 mb-2">
          Welcome to Zaman AI Assistant
        </h1>
        <p className="text-gray-600 mb-8">
          Your personal Islamic finance expert. Ask me anything about Islamic finance principles, investment options, or financial planning.
        </p>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {exampleQueries.map((query, index) => (
          <QueryCard
            key={index}
            title={query.title}
            description={query.description}
            onClick={onQueryClick}
          />
        ))}
      </div>
    </div>
  );
};