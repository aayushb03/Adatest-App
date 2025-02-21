import React, {useState} from "react";
import {ThreeDots} from "react-loading-icons";

type ResetTestsProps = {
  resetTests: (config : "AIBAT" | "Mini-AIBAT" | "M-AIBAT", name: string) => void;
  isResetting: boolean;
}

const ResetTests = ({resetTests, isResetting} : ResetTestsProps) => {
  const [name, setName] = useState<string>('');

  return (
    <div className={'w-full h-full flex flex-col'}>
      <div className={"text-2xl p-2 font-light w-full text-center"}>Reset Tests</div>
      <div className={"w-full h-full flex flex-col items-center justify-center"}>
        <div className={"text-xl w-full text-center text-red-500"}>Are you sure you want to end this session?</div>
        <div className={"text-xl w-full text-center text-red-500"}>The following actions will reset all tests.</div>
        <div className={"text-xl w-full text-center text-red-500"}>Please exit the popup to cancel.</div>
        <div className={"justify-center mt-8 flex flex-row "}>
          <div className={"text-xl w-full"}>Name:</div>
          <input type={'text'} onChange={(e) => setName(e.target.value.replace(/\s+/g, ''))} value={name} className={"w-64 h-8 rounded-md border border-gray-500"} />
        </div>
        <div className={"text-xl w-full text-center mt-8"}>Select one of the following configurations for AIBAT</div>
        <div className={"flex gap-8 mt-4 justify-center"}>
          <div className={"flex flex-col justify-center items-center"}>
            <button
              className={`flex h-8 w-32 items-center justify-center rounded-md bg-gray-700 font-light text-white shadow-2xl ${isResetting ? 'disabled cursor-not-allowed' : 'cursor-pointer transition hover:scale-105 hover:bg-gray-900'}`}
              onClick={() => {if(!isResetting && name) resetTests("AIBAT", name)}}>
              {isResetting ?
                <ThreeDots className="h-3 w-8" /> :
                'AIBAT'
              }
            </button>
            <div className={"text-center text-sm text-gray-500"}>Base AIBAT - Includes INV and DIR criteria</div>
          </div>
          <div className={"flex flex-col justify-center items-center"}>
            <button
              className={`flex h-8 w-32 items-center justify-center rounded-md bg-gray-700 font-light text-white shadow-2xl ${isResetting ? 'disabled cursor-not-allowed' : 'cursor-pointer transition hover:scale-105 hover:bg-gray-900'}`}
              onClick={() => {if(!isResetting && name) resetTests("Mini-AIBAT", name)}}>
              {isResetting ?
                <ThreeDots className="h-3 w-8" /> :
                'Mini-AIBAT'
              }
            </button>
            <div className={"text-center text-sm text-gray-500"}>Mini AIBAT - Includes only INV criteria</div>
          </div>
          <div className={"flex flex-col justify-center items-center"}>
            <button
              className={`flex h-8 w-32 items-center justify-center rounded-md bg-gray-700 font-light text-white shadow-2xl ${isResetting ? 'disabled cursor-not-allowed' : 'cursor-pointer transition hover:scale-105 hover:bg-gray-900'}`}
              onClick={() => {if(!isResetting && name) resetTests("M-AIBAT", name)}}>
              {isResetting ?
                <ThreeDots className="h-3 w-8" /> :
                'M-AIBAT'
              }
            </button>
            <div className={"text-center text-sm text-gray-500"}>Multilingual AIBAT - Includes multilingual criteria</div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ResetTests;