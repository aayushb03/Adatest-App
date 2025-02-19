"use client";

import TestList from "@/app/components/TestList";
import TaskGraph from "@/app/components/TaskGraph";
import {useState, useEffect, useContext} from "react";
import {generateTests, getPrompt, resetDB} from "@/lib/Service";
import {testDataType} from "@/lib/Types";
import {TestDataContext} from "@/lib/TestContext";
import RadioButtons from "@/app/components/RadioButtons";
import Buttons from "@/app/components/Buttons";
import {fetchTests} from "@/lib/utils";
import {v4 as uuidv4} from "uuid";

export default function Home() {
  const [sessionIdSet, setSessionIdSet] = useState(false);

  // Boolean for if the tests are being generated
  const [isGenerating, setIsGenerating] = useState(false);
  // Boolean for if perturbations are being generated
  const [isPerturbing, setIsPerturbing] = useState(false);
  // String for the current topic prompt
  const [topicPrompt, setTopicPrompt] = useState<string>("");

  // Map that contains all current filters ('' is no filter)
  // 'label' -> (un)acceptable
  // 'grade' -> (dis)agreed, ungraded
  // 'pert' -> type of perturbation
  const [filterMap, setFilterMap] = useState<{ [key: string]: string }>({
    label: "",
    grade: "",
    pert: "",
  });

  // Boolean for if first checkbox is auto-selected
  const [isAutoCheck, setIsAutoSelect] = useState<boolean>(false);

  // Load test decision context
  const {
    testData,
    setTestData,
    currentTopic,
    setCurrentTopic,
    isCurrent,
    setIsCurrent,
  } = useContext(TestDataContext);

  /**
   * Generate session ID for the user
   */
  useEffect(() => {
    if (!localStorage.getItem("sessionId")) {
      localStorage.setItem("sessionId", uuidv4());
    }
    resetDB('AIBAT').catch();
    setSessionIdSet(true);
  }, []);

  /**
   * Load in new tests when they are changed
   */
  useEffect(() => {
    if (!localStorage.getItem("sessionId")) return;
    fetchTests(
      filterMap,
      currentTopic,
      isAutoCheck,
      testData,
      setTestData,
      setIsCurrent,
      setCurrentTopic,
    ).catch();
  }, [isCurrent, currentTopic, filterMap, isAutoCheck, isPerturbing, sessionIdSet]);

  /**
   * Update displayed tests when the topic changes
   */
  useEffect(() => {
    if (!localStorage.getItem("sessionId")) return;
    let newTestsData: testDataType = {
      tests: testData.tests,
      currentTests: testData.tests[currentTopic],
      test_decisions: testData.test_decisions,
      pert_decisions: testData.pert_decisions,
    };
    setTestData(newTestsData);
    getPrompt(currentTopic).then((prompt) => {
      setTopicPrompt(prompt);
    });
  }, [currentTopic, isCurrent, sessionIdSet]);

  /**
   * Generate tests for the current topic
   */
  async function onGenerateTests() {
    setIsGenerating(true);
    await generateTests(currentTopic);
    setIsGenerating(false);
    return;
  }

  return (
    <div className={"grid grid-cols-4"}>
      {sessionIdSet && <>
        <div
          className={
            "col-span-1 p-4 h-screen justify-center w-full border-gray-500 border"
          }
        >
          <TaskGraph/>
        </div>
        <main className="col-span-3 flex w-full h-screen flex-col items-center">
          {/* HEADER */}
          <div className={"px-4 w-full h-20 flex gap-2 items-center py-1"}>
            <span className={"text-3xl font-light"}>Topic:</span>
            <RadioButtons
              isAutoCheck={isAutoCheck}
              setIsAutoCheck={setIsAutoSelect}
            />
          </div>
          <div className={"px-4 w-full py-1 h-24 flex items-center gap-2"}>
            <div className={"font-bold"}>Prompt:</div>
            <div className={"italic"}>&quot;{topicPrompt}&quot;</div>
          </div>
          <TestList filterMap={filterMap} setFilterMap={setFilterMap}/>
          <Buttons
            currentTopic={currentTopic}
            isGenerating={isGenerating}
            genTests={onGenerateTests}
            isPerturbing={isPerturbing}
            setIsPerturbing={setIsPerturbing}
          />
        </main>
      </>}
    </div>
  );
}
