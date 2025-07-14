import React from "react";  // needed for React-specific components - like React.FC

interface FetchApp2RootProps {
    onFetch: () => void;
    result: string;
}

const FetchApp2Root: React.FC<FetchApp2RootProps> = ({
    onFetch,
    result
}) => (
    <div>
        <button onClick={onFetch}>Fetch / (app2 root)</button>
        <div>{result}</div>
    </div>
);

export default FetchApp2Root;