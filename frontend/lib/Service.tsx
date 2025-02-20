import { perturbedTestType, testType } from "@/lib/Types";

export async function checkSession() {
  const url = `core/session/check/${localStorage.getItem("sessionId")}`;
  try {
    const res = await fetch(url, {
      method: 'GET',
      cache: "no-store",
    });
    return await res.json();
  } catch (error) {
    console.error(error);
  }
}

export async function getAppConfig() {
  const url = `core/session/get/${localStorage.getItem("sessionId")}`;
  try {
    const res = await fetch(url, {
      method: 'GET',
      cache: "no-store",
    });
    return await res.json();
  } catch (error) {
    console.error(error);
  }
}

/**
  * Gets an array of tests based off of the topic
  * @param topic PE, KE, or LCE
  * @returns An array of tests
  */
export async function getTests(topic: string) {
  const url = `core/tests/get/${topic}/${localStorage.getItem("sessionId")}`;
  try {
    const res = await fetch(url, {
      cache: "no-store",
    });
    // checks that the response is valid
    if (!res.ok) {
      throw new Error("Failed to get tests");
    }
    // creates and maps an array of Test Objects
    return await res.json();
  } catch (error) {
    console.error(error);
  }
}

/**
  * Generates tests for the given topic
  * @param topic PE, KE, or LCE
  * @returns all tests for the topic
  */
export async function generateTests(topic: string) {
  const url = `core/tests/post/${topic}/${localStorage.getItem("sessionId")}`
  try {
    await fetch(url, {
      method: 'POST',
      cache: "no-store",
      body: JSON.stringify({ topic }),
    });
    return await getTests(topic);
  } catch (error) {
    console.error(error);
  }
}

/**
 * Decides on a list of tests based on the decision and topic
 * @param tests List of tests to be decided
 * @param decision Approved, Denied, Invalid
 * @param topic Current topic being worked on
 */
export async function processTests(tests: testType[], decision: string, topic: string) {
  if (tests.length === 0) return;
  const url = `core/tests/process/${decision}/${topic}/${localStorage.getItem("sessionId")}`;
  try {
    await fetch(url, {
      method: 'POST',
      body: JSON.stringify(tests),
    });
  } catch (e) {
    console.error(e);
  }
}


export async function logAction(test_ids: string[], action: string) {
  const url = `core/logs/add/${localStorage.getItem("sessionId")}`;
  let tests = ""
  test_ids.forEach((test_id) => {
    tests += test_id + ","
  });
  const data = {
    test_ids: tests,
    action: action
  }
  try {
    await fetch(url, {
      method: 'POST',
      cache: "no-store",
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ data }),
    });
  } catch (error) {
    console.error(error);
  }
}

export async function saveLogs() {
  const url = `core/logs/save/${localStorage.getItem("sessionId")}`;
  try {
    await fetch(url, {
      method: 'POST',
      cache: "no-store",
    });
  } catch (error) {
    console.error(error);
  }
}


/**
 * Reset the tests in the database
 * Calls clear then init
 */
export async function resetDB(config: "AIBAT" | "Mini-AIBAT" | "M-AIBAT") {
  try {
    await fetch(`core/tests/clear/${config}/${localStorage.getItem("sessionId")}`, {
      method: 'DELETE',
      cache: 'no-store',
    });
    await fetch(`core/tests/init/${localStorage.getItem("sessionId")}`, {
      method: 'POST',
      cache: 'no-store'
    });
  } catch (error) {
    console.error(error);
  }
}

/**
  * creates perturbations for the given tests
  * @param tests List of tests to be approved
  * @param topic PE, KE, LCE
  */
export async function createPerturbations(tests: testType[], topic: string) {
  if (tests.length === 0) return;
  const url = `core/perturbations/generate/${topic}/${localStorage.getItem("sessionId")}`;
  try {
    const perturbations = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      cache: 'no-store',
      body: JSON.stringify(tests),
    });
    return await perturbations.json()
  } catch (e) {
    console.error(e);
  }
}

/**
  * Gets an array of perturbations based off of the topic
  * @param topic PE, KE, or LCE
  * @returns An array of perturbations
  */
export async function getPerturbations() {
  const url = `core/perturbations/get/${localStorage.getItem("sessionId")}`;
  try {
    const res = await fetch(url, {
      method: 'GET',
      cache: "no-store",
    });
    // checks that the response is valid
    if (!res.ok) {
      throw new Error("Failed to get perturbations");
    }
    // creates and maps an array of Test Objects
    return await res.json();
  } catch (error) {
    console.error(error);
  }
}

export async function getDefaultPerturbations(appConfig: string) {
  const url = `core/perturbations/getDefault/${appConfig}`;
  try {
    const res = await fetch(url, {
      method: 'GET',
      cache: "no-store",
    });
    return await res.json();
  } catch (error) {
    console.error(error);
  }
}


/**
 * Adds a test to the database
 * @param test
 * @param topic
 * @param groundTruth
 */
export async function addTest(test: testType, topic: string, groundTruth: string) {
  const url = `core/tests/add/${topic}/${groundTruth}/${localStorage.getItem("sessionId")}`;
  try {
    await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ test }),
    });
  } catch (error) {
    console.error(error);
  }
}

/**
 * Edits a test in the database
 * @param test
 * @param topic
 */
export async function editTest(test: testType | perturbedTestType, topic: string, isPert: boolean = false) {
  const url = `core/${isPert ? 'perturbations' : 'tests'}/edit/${topic}/${localStorage.getItem("sessionId")}`;
  try {
    await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ test }),
    });
  } catch (error) {
    console.error(error);
  }
}

/**
 * Deletes a test from the database
 * @param tests List of perturbed tests to be validated
 * @param validation Approved, Denied, Invalid
 */
export async function validatePerturbations(tests: perturbedTestType[], validation: string) {
  const url = `core/perturbations/validate/${validation}/${localStorage.getItem("sessionId")}`;
  try {
    await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(tests),
    });
  } catch (error) {
    console.error(error);
  }
}

/**
 * Creates a new perturbation type
 * @param tests List of tests to be perturbed
 * @param type Type of perturbation (e.g. synonyms, spelling, etc.)
 * @param prompt AI Prompt
 * @param testDirection Direction of the test(INV, DIR)
 * @param topic Topic of the perturbation
 * @returns List of perturbed tests
 */
export async function addNewPerturbation(tests: testType[], type: string, prompt: string, testDirection: string) {
  const url = `core/perturbations/add/${localStorage.getItem("sessionId")}`;
  try {
    const res = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        test_list: tests,
        prompt: prompt,
        flip_label: testDirection === 'DIR',
        pert_name: type,
      }),
    });
    return await res.json();
  } catch (error) {
    console.error(error);
  }
}

/**
 * Tests the new perturbation type
 * @param type Type of perturbation (e.g. synonyms, spelling, etc.)
 * @param prompt AI Prompt
 * @param statement Statement to test
 * @param direction Direction of the test(INV, DIR)
 * @param topic Topic of the perturbation
 * @returns A perturbed test object
 */
export async function testNewPerturbation(type: string, prompt: string, statement: string, direction: string) {
  const url = `core/perturbations/test/${localStorage.getItem("sessionId")}`;
  try {
    const res = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        test_case: statement,
        prompt: prompt,
        flip_label: direction === 'DIR',
        pert_name: type,
      }),
    });
    return await res.json();
  } catch (error) {
    console.error(error);
  }
}

/**
 * Deletes a perturbation type
 * @param type perturbation type to delete
 * @returns all perturbations
 */
export async function deletePerturbation(type: string) {
  const url = `core/perturbations/delete/${localStorage.getItem("sessionId")}`;
  try {
    const res = await fetch(url, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        pert_name: type,
      }),
    });
    return await res.json();
  } catch (error) {
    console.error(error);
  }
}

/**
 * Gets a pert type
 * @param type Type of perturbation (e.g. synonyms, spelling, etc.)
 * @returns A perturbation type object
 */
export async function getPerturbationInfo(type: string) {
  const url = `core/perturbations/getType/${type}/${localStorage.getItem("sessionId")}`;
  try {
    const res = await fetch(url, {
      method: 'GET',
      cache: "no-store",
    });
    return await res.json();
  } catch (error) {
    console.error(error);
  }
}

/**
 * Gets all pert types
 * @returns An array of perturbation types
 */
export async function getAllPerturbationTypes() {
  const url = `core/perturbations/getAll/${localStorage.getItem("sessionId")}`;
  try {
    const res = await fetch(url, {
      method: 'GET',
      cache: "no-store",
    });
    return await res.json();
  } catch (error) {
    console.error(error);
  }
}

/**
 * Edits a perturbation type
 * @param tests List of tests to be perturbed
 * @param type Type of perturbation (e.g. synonyms, spelling, etc.)
 * @param prompt AI Prompt
 * @param testDirection Direction of the test(INV, DIR)
 * @param topic Topic of the perturbation
 * @returns List of perturbed tests
 */
export async function editPerturbation(tests: testType[], type: string, prompt: string, testDirection: string) {
  await deletePerturbation(type);
  return await addNewPerturbation(tests, type, prompt, testDirection);
}

/**
 * Gets all topics
 * @returns A string array of topics
 */
export async function getTopics() {
  const url = `core/topics/get/${localStorage.getItem("sessionId")}`;
  try {
    const res = await fetch(url, {
      method: 'GET',
      cache: "no-store",
    });
    return await res.json();
  } catch (error) {
    console.error(error);
  }
}

/**
 * Gets prompt for a topic
 * @param topic Topic to get prompt for
 * @returns A string of the prompt
 */
export async function getPrompt(topic: string) {
  const url = `core/topics/prompt/${topic}/${localStorage.getItem("sessionId")}`;
  try {
    const res = await fetch(url, {
      method: 'GET',
      cache: "no-store",
    });
    return await res.json();
  } catch (error) {
    console.error(error);
  }
}

/**
 * Adds a topic
 * @param topic Topic to add (shorthand)
 * @param prompt_topic Topic to add (full name that will go in the prompt)
 * @param tests List of tests to add in the format {test: string, ground_truth: string}
 */
export async function addTopic(topic: string, prompt_topic: string, tests: { test: string, ground_truth: string }[]) {
  const url = `core/topics/add/${localStorage.getItem("sessionId")}`;
  try {
    await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ topic, prompt_topic, tests }),
    });
  } catch (error) {
    console.error(error);
  }
}

/**
 * Deletes a topic
 * @param topic Topic to delete
 */
export async function deleteTopic(topic: string) {
  const url = `core/topics/delete/${localStorage.getItem("sessionId")}`;
  try {
    await fetch(url, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ topic }),
    });
  } catch (error) {
    console.error(error);
  }
}

/**
 * Tests a prompt on a test
 * @param prompt Prompt to test
 * @param test Test to test
 * @returns A test object
 */
export async function testTopicPrompt(prompt: string, test: string) {
  const url = 'core/topics/test';
  try {
    const res = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ prompt, test }),
    });
    return await res.json();
  } catch (e) {
    console.error(e);
  }
}

