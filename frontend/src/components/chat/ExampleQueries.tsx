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
      title: "Какая ожидаемая доходность по \"Вакала Zaman\" и на какие сроки доступен депозит? Можно ли пополнять после открытия?",
      description: "Узнайте о доходности и условиях депозита Vakala Zaman"
    },
    {
      title: "Сколько стоит обслуживание: выпуск, первый год, со второго года? На какой срок выпускается карта?",
      description: "Информация о стоимости обслуживания и сроках действия карт"
    },
    {
      title: "Что такое наценка в исламском банкинге и почему это не проценты (риба)? Почему она фиксирована?",
      description: "Понимание концепции наценки в исламском финансировании"
    },
    {
      title: "Я ИП: хочу открыть точку на 10 000 000 ₸. Сравни ежемесячные платежи на 36 vs 60 мес и сформируй список документов/шагов.",
      description: "Расчет платежей и необходимые документы для открытия точки ИП"
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
      <div className="grid grid-cols-1 gap-4 max-w-6xl mx-auto">
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