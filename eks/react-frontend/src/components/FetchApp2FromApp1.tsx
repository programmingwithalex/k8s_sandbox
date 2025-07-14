import React from "react";  // needed for React-specific components - like React.FC

interface FetchApp2FromApp1Props {
    onFetch: () => void;
    result: string;
}

const FetchApp2FromApp1: React.FC<FetchApp2FromApp1Props> = ({
    onFetch,
    result
}) => (
    <div>
        <button onClick={onFetch}>Fetch / (app1/read_app2)</button>
        <div>{result}</div>
    </div>
);

export default FetchApp2FromApp1;