import React from "react";  // needed for React-specific components - like React.FC

interface FetchApp1RootProps {
    onFetch: () => void;
    result: string;
}

const FetchApp1Root: React.FC<FetchApp1RootProps> = ({
    onFetch,
    result
}) => (
    <div>
        <button onClick={onFetch}>Fetch / (app1 root)</button>
        <div>{result}</div>
    </div>
);

export default FetchApp1Root;