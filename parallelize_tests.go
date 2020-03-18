// Copyright 2020 Google LLC.
//
// Use of this source code is governed by a BSD-style
// license that can be found in the LICENSE file or at
// https://developers.google.com/open-source/licenses/bsd

package main

import (
	"context"
	"errors"
	"math/rand"
	"os"
	"os/exec"
	"os/signal"
	"runtime"
	"strings"
	"sync"

	"github.com/orijtech/otils"
)

func main() {
	testApps := otils.NonEmptyStrings(strings.Split(os.Getenv("DJANGO_TEST_APPS"), " ")...)
	if len(testApps) == 0 {
		panic("No DJANGO_TEST_APPS passed in")
	}

	rand.Shuffle(len(testApps), func(i, j int) {
		testApps[i], testApps[j] = testApps[j], testApps[i]
	})

	// Otherwise, we'll parallelize the builds.
	nParallel := runtime.GOMAXPROCS(0)
	println(nParallel)

	shutdownCtx, cancel := context.WithCancel(context.Background())
	defer cancel()

	// Gracefully shutdown on Ctrl+C.
	sigCh := make(chan os.Signal, 1)
	signal.Notify(sigCh, os.Interrupt)
	go func() {
		<-sigCh
		cancel()
	}()

	var wg sync.WaitGroup
	defer wg.Wait()

	// Now run the tests in parallel.
	stride := len(testApps) / nParallel
	if stride <= 0 {
		stride = 1
	}
	for i := 0; i < len(testApps); i += stride {
		apps := testApps[i : i+stride]
		wg.Add(1)
		go runTests(shutdownCtx, &wg, apps, "django_test_suite.sh")
	}
}

func runTests(ctx context.Context, wg *sync.WaitGroup, djangoApps []string, testSuiteScriptPath string) error {
	defer wg.Done()

	if len(djangoApps) == 0 {
		return errors.New("Expected at least one app")
	}

	cmd := exec.CommandContext(ctx, "bash", testSuiteScriptPath)
	cmd.Env = append(os.Environ(), `DJANGO_TEST_APPS=`+strings.Join(djangoApps, " ")+``)
	cmd.Stderr = os.Stderr
	cmd.Stdout = os.Stdout
	if err := cmd.Run(); err != nil {
		panic(err)
	}
	return nil
}
